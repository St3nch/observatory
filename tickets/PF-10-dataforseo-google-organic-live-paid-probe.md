# PF-10 — DataForSEO Google Organic Live Advanced bounded paid probe

**Status:** review
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** provider adapter / bounded paid contract probe
**Blocked by:** PF-09 closed; Steward transition to `ready`; live operator run additionally
blocked by fresh pricing review, text-retention/terms acceptance, an accepted bounded F6
off-host protection path, and explicit [CHAZ] authorization
**Approved by:** Project Steward for implementation only; live provider invocation remains separately gated below
**Start commit:** `34c083474b4e1fbf8d0c3b84ab0eb210476e0976`

## What to build

Add one exact DataForSEO production adapter contract for Google Organic Live Advanced so
Observatory can preserve one real point-in-time SERP as Evidence. The adapter is a bounded
learning probe, not recurring rank tracking and not standing authorization for Google SERP
collection.

The accepted contract is one HTTP POST, one task, one keyword, one Capture at most, no
retry, no redirect follow-up, no polling, and no automatic second request. It reuses the
accepted HTTP event-v2 Evidence boundary and PF-09 bounded single-exchange substrate while
keeping all request, spend, target, and authorization semantics adapter-owned.

## Provider contract snapshot used to cut this ticket

Steward verified the official DataForSEO Google Organic Live Advanced documentation and
pricing on 2026-08-18. The provider currently documents:

- production POST path `/v3/serp/google/organic/live/advanced`;
- exactly one task per Live SERP API call;
- `depth` default 10 and maximum 200;
- Google Organic Live billing per 10-result SERP, with depth above 10 increasing cost;
- Live base price of $0.002 per 10-result SERP at the verified snapshot;
- `load_async_ai_overview=true` as a separately priced option intended to retrieve an
  asynchronously loaded AI Overview when available;
- Advanced results containing point-in-time SERP context plus heterogeneous items with
  provider-native item type, `rank_group`, `rank_absolute`, page/position and, by item type,
  exact URLs/domains and other source relationships.

Provider documentation and pricing are external and mutable. These statements justify this
planned contract only. A live command requires a fresh Steward recheck and stops if the
current claimed contract or price no longer fits the ceiling below.

## Authority

- D8 — Attempt/Capture Evidence boundary and verify-on-read remain unchanged.
- D9 — HTTP event v2, committed credential-free request, no redirect follow-up,
  secret-header omission, and one-exchange discipline.
- D12 — this is one materially distinct adapter contract and Provider contract probe;
  claimed documentation is not the Derivation contract and one payload proves existence,
  not invariance.
- D13 — Google SERP composition is materially useful product-direction testimony, while
  this adapter remains separately bounded and authorized.
- F3 remains unfired for routine broad rollout.
- F6 remains deferred generally; a separately accepted bounded off-host protection sequence
  is required for this irreplaceable probe.
- F7 remains deferred; one operator / one process only.
- F9 remains deferred; no HTTP write API.
- F12 remains deferred; no query-panel ownership, cadence, scheduler, or recurring capture.

## Exact adapter contract

Use adapter contract token:

`dataforseo-serp-google-organic-live-advanced-paid-probe-v1`

Provider is exactly `dataforseo`. Production target is exactly:

`POST https://api.dataforseo.com/v3/serp/google/organic/live/advanced`

The request contains exactly one task. The public capture CLI accepts one `--keyword` plus
the exact spend acknowledgement and Evidence-root inputs already customary for bounded
provider probes. It accepts no caller-supplied URL, host, path, location, language, device,
OS, depth, headers, timeout, enrichment toggle, retry setting, task JSON, or alternate spend
ceiling.

The task is closed to:

- `keyword`: one operator-supplied natural-language query, 1..80 printable ASCII characters,
  at most 10 words; reject DataForSEO-documented search-operator forms that multiply price;
- `location_code`: exactly `2840` (United States);
- `language_code`: exactly `en`;
- `depth`: exactly `100`;
- `device`: exactly `desktop`;
- `os`: exactly `windows`;
- `load_async_ai_overview`: exactly `true`;
- `group_organic_results`: exactly `true`.

Do not send `stop_crawl_on_match`, `max_crawl_pages`, `search_param`, `remove_from_url`,
`people_also_ask_click_depth`, `calculate_rectangles`, browser-size overrides, `tag`, or
another optional request parameter in this contract.

Those omissions are deliberate. In particular:

- exact provider-returned URLs must not be rewritten by request option;
- PAA expansion and pixel/rectangle acquisition materially change cost/response testimony
  and remain later contract branches;
- depth 101..200 is deliberately not acquired by this first probe; revisit only if the
  additional ranking horizon proves materially worth its recurring acquisition cost.

Request-body bytes are the exact deterministic UTF-8 JSON/JCS form selected by the adapter
contract and installed before Attempt commit. Credentials are injected only inside transport
after the committed Attempt is read back and verified.

## Spend boundary

At the 2026-08-18 pricing snapshot, depth 100 represents up to ten priced 10-result SERPs at
$0.002 each, and the documented async-AI-Overview option may add $0.002. The Attempt records
an authorization ceiling of exactly **30,000 micro-USD ($0.03)** and a dated pricing-basis
token for this contract.

The public command requires exact `--authorize-max-micro-usd 30000`. This is [CHAZ]'s
authorization ceiling, not a provider-enforced invoice guarantee. If a fresh pricing/contract
recheck cannot establish that the closed request remains safely below the ceiling, do not
create the Attempt and do not send.

Reject a store that already contains a committed Attempt for this exact paid-probe adapter.
No automatic retry is allowed after Attempt creation, including unresolved/no-response or
partial-response outcomes. Any second real exchange requires a new Steward/[CHAZ]
authorization decision.

## Response bound and transport

The adapter-owned response-body ceiling is exactly `33_554_432` bytes (32 MiB). This is a
bounded safety ceiling for this rich Advanced SERP probe, not a global Observatory default or
a claim about provider maximum response size.

PF-09 owns the shared streaming mechanics. This adapter owns the 32 MiB value and passes it
internally; it must not become a CLI/API parameter. Exceeding the ceiling yields the existing
HTTP-v2 `response_partial` testimony with the exact retained prefix and closed receive-body
failure semantics. Do not invent a new transport enum merely for this adapter.

Use the existing DataForSEO credential boundary and Basic Authorization injection. Keep
`trust_env=False`, redirects disabled, and no hidden provider preflight/account/catalog call.

## Event-v2 integration

Extend the recognized HTTP event-v2 adapter set only enough to validate this third exact
contract. Do not introduce a generic dynamic adapter registry.

The adapter-specific validator closes its own request, parameters, policy and body equation.
Existing fixture, sandbox, and Keyword Overview event-v1/v2 bytes and identities remain
unchanged. Mixed stores containing the new adapter remain healthy; unrelated Derivations
skip it unless and until a Google Organic recipe is accepted.

## Probe is Evidence-only

This ticket emits no Google Organic Outcome, Observation, PostgreSQL detail row, history API,
generic SERP API, ranking score, strategy result, or cross-surface entity mapping.

A service-owned read-only inspection command may accept only Evidence root + Capture ID,
require a verified complete Capture from this exact adapter, and emit the exact response body
for Steward/[CHAZ] inspection. It performs no network, retry, normalization, summary,
Derivation, or persistence.

## Pre-send retention / terms gate

Google Organic Advanced may return snippets, AI Overview answer/source text, URLs, images or
other third-party SERP content. Because Capture body Evidence is immutable, the real probe is
not authorized merely by completing the code.

Before the live command, the Steward must explicitly record acceptance that retaining this
closed provider response as Observatory Evidence is acceptable for the bounded probe under
the current provider terms, privacy/personal-data posture, and intended API-redistribution
boundary. If that gate is not accepted, do not send.

## Acceptance criteria — implementation commit

- [x] Third exact HTTP-v2 adapter token is recognized without weakening the two existing
      adapter contracts or introducing generic endpoint execution.
- [x] Closed request contains exactly the task fields/values above and one keyword.
- [x] Public CLI cannot alter target, context, depth, enrichment flags, headers, timeout,
      response limit, retry behavior, or spend ceiling.
- [x] Exact 30,000 micro-USD authorization acknowledgement is required before Attempt commit.
- [x] Store-level one-shot guard refuses a second Attempt for this probe adapter.
- [x] Committed Attempt precedes any transport and exact request bytes are read-back verified.
- [x] PF-09 shared transport is used with adapter-owned 32 MiB bound.
- [x] Complete/partial/no-response branches preserve existing HTTP-v2 semantics.
- [x] Credentials and secret-class response-header values cannot enter Evidence or emitted
      errors/output.
- [x] Capture is committed and verify-on-read checked when transport testimony exists.
- [x] Inspection refuses wrong adapter, partial/no-response, malformed/tampered Evidence and
      performs no mutation/network.
- [x] Existing sandbox and Keyword Overview conformance vectors/digests remain unchanged.
- [x] Existing fixture/provider Derivations do not create rows for this Evidence-only adapter.
- [x] No provider network, DNS, credentials, or spend occurs in ordinary tests/review.
- [x] `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` are green.

## Required tests

- Exact request parameters/body/fingerprint/Attempt deterministic vector for this adapter.
- Structural Attempt-before-send capability gate and fabricated/used-capability rejection.
- Exact target and internal loopback-only path validation.
- Public CLI argument-surface refusal for arbitrary endpoint/context/options.
- Spend acknowledgement absent/wrong/bool/alternate ceiling fails before Attempt creation.
- Second paid-probe Attempt in one store is refused before transport.
- Shared-transport complete, partial, limit-exceeded, no-response and credential-leak
  regressions through this adapter.
- 32 MiB value is adapter-owned; deterministic tests may substitute the shared seam with a
  small bound rather than allocating a 32 MiB response solely to prove parameterization.
- Secret response-header omission and retained-header order/duplicate proof.
- Capture read-back/body identity verification and tamper refusal.
- Inspection wrong-adapter/partial/no-response/tamper refusal and exact complete-body output.
- Mixed-store scrub and fixture/Keyword-Overview derivation regressions.
- Existing D9/D10 published conformance vectors recompute unchanged.

## Live closure gate — not implementation authorization

After GROK's zero-network implementation commit is independently accepted, the Steward may
issue one exact operator command only after all of the following are fresh and explicit:

1. current official endpoint/request contract rechecked;
2. current official pricing rechecked against the exact closed task and $0.03 ceiling;
3. retention/privacy/provider-terms/API-redistribution gate accepted;
4. bounded off-host Evidence protection path accepted for this probe;
5. [CHAZ] explicitly authorizes the one-shot command.

The operator run uses a fresh Evidence root. After the run: inspect/scrub the source,
record exact Attempt/Capture IDs, protect the full Evidence root off-host under the accepted
bounded procedure, restore to a fresh local root, scrub, and prove exact committed-ID set
equality. No retry or second provider exchange is implied by failure at any stage.

## Out of scope

- Google Organic Derivation Recipe, parser, typed SERP Observations, or read API
- recurring rank tracking, scheduling, query panels, or F12 orchestration
- Google AI Mode as its own surface
- PAA click expansion, pixel/rectangle capture, depth >100, mobile/macOS/iOS variants
- Standard/task-post/task-get SERP workflows or any multi-exchange provenance
- generic provider adapter registry or arbitrary HTTP runner
- URL normalization, universal Page ID, strategy labels, opportunity scoring
- F7 concurrency, F8 production API auth, F9 HTTP writes, F10 projections
- Firecrawl, OnPage, YouTube, backlinks, LLM Mentions, or another provider surface

## One implementation commit must prove

Observatory can add one production DataForSEO Google Organic Live Advanced paid-probe
contract on the shared bounded one-exchange substrate without weakening Evidence identity,
adapter isolation, spend authorization, or existing provider behavior, while remaining
zero-network until a separately authorized live operator probe.

## Implementer report requirements

GROK must explicitly report:

- exact adapter token, request bytes/digest, fingerprint, and deterministic Attempt vector;
- exact public CLI surface and pre-Attempt spend/target gates;
- the shared-vs-adapter transport ownership split inherited from PF-09;
- proof the 32 MiB limit is private adapter policy and no global default changed;
- every existing conformance digest/ID checked unchanged;
- all code paths capable of network I/O and why ordinary tests cannot reach a real provider;
- the weakest part of the adapter design and any contract ambiguity he intentionally did not
  guess around.

## Steward amendment after adversarial review

This amendment is normative for PF-10 and closes the identity, spend-grammar, timeout, and
grouping decisions that the original planned text left implicit.

### Closed keyword grammar

`keyword` is one string of 1..80 printable ASCII characters and at most 10 words. A word is
a maximal nonempty run separated by ASCII space. The keyword begins and ends with an ASCII
alphanumeric. Internal characters are limited to:

`A-Z a-z 0-9 space & ' ( ) + , . / : -`

After lowercasing the ASCII keyword, reject it before Attempt creation if it contains any of
these substrings anywhere:

`allinanchor:`, `allintext:`, `allintitle:`, `allinurl:`, `cache:`, `define:`,
`definition:`, `filetype:`, `id:`, `inanchor:`, `info:`, `intext:`, `intitle:`,
`inurl:`, `link:`, `related:`, `site:`.

This intentionally conservative deny set is the union needed to fail safely across the
current official Google Organic Live/Advanced documentation and pricing/help material, whose
operator lists are not perfectly consistent. It also rejects prefixed forms such as
`-site:` because they contain `site:`. A fresh provider-price review may stop the probe if
the provider contract changes; it may not silently widen this grammar. A different grammar
requires an amended adapter contract.

### Exact identity-bearing envelope

The closed `parameters` object has exactly these keys and values:

- `contract`: `dataforseo-serp-google-organic-live-advanced-paid-probe-v1`
- `keyword`: the validated operator-supplied keyword above
- `location_code`: `2840`
- `language_code`: `en`
- `depth`: `100`
- `device`: `desktop`
- `os`: `windows`
- `load_async_ai_overview`: `true`
- `group_organic_results`: `true`

The provider task is exactly `parameters` without `contract`. Request-body bytes are UTF-8
JCS of a singleton array containing that task, with no trailing newline.

The closed `policy` object has exactly these keys and values:

- `max_authorized_cost_micro_usd`: `30000`
- `mode`: `paid_probe`
- `policy_version`: `dataforseo-google-organic-live-paid-probe-v1`
- `pricing_basis`: `dataforseo-google-organic-live-2026-08-18`

The one-shot guard is keyed by the exact adapter contract, not by `policy.mode`; a store that
contains Keyword Overview paid-probe Evidence does not thereby block this distinct probe.

### Adapter-owned timeout and response bound

PF-10 owns the production timeout profile:

`httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)`

PF-10 also owns the planned `33_554_432` byte response-body ceiling. Both values are private
adapter policy passed to the PF-09 seam. Neither is a CLI/API/user-controlled option or an
Observatory-wide default. No retry is authorized after any committed Attempt.

### Grouping and completeness semantics

`group_organic_results=true` is identity-bearing request context. Under the current claimed
provider contract, related results are nested as `related_result` snippets of their parent
organic item; `false` would promote them to separate organic items and can change result
cardinality and later rank interpretation. `false` is therefore a materially distinct future
contract branch, not an omitted sample of this adapter.

`depth=100` is requested provider parse depth, not a promise of 100 organic rows and not a
universal historical-completeness claim. A transport-complete HTTP response can legitimately
contain fewer organic items and heterogeneous SERP features. Any later Derivation must model
provider-returned counts/context from Evidence rather than infer completeness from depth.

### Public and loopback seams

The implementation module is exactly `observatory.dataforseo_google_organic_paid_probe`.

Its public `capture` subcommand requires `--evidence-root`, exactly one `--keyword`, and
exact `--authorize-max-micro-usd 30000`. Its public `inspect` subcommand requires
`--evidence-root` and one `--capture-id`. Neither public subcommand accepts an endpoint,
timeout, response ceiling, provider options, task JSON, headers, location/language/device,
or alternate spend ceiling.

The internal deterministic loopback override accepts only the loopback host
`127.0.0.1`, an explicit test port, and the exact path
`/v3/serp/google/organic/live/advanced`; it is unreachable from the public CLI.

### Explicit non-acquisition / revisit triggers

- `group_organic_results=false`: revisit only if separately ranked related-result cardinality
  is materially required.
- mobile/macOS/iOS variants: revisit when device-specific SERP divergence is a deliberate
  measurement requirement.
- explicit `se_domain`: revisit when provider-selected domain from location/language is
  insufficient for a deliberate country/domain comparison.
- `search_param` or time-filtered search context: revisit when a bounded time/search-mode
  comparison is deliberately required.
- depth 101..200, PAA expansion, rectangles, target/stop-crawl, URL input/rewriting, and
  other optional fields remain separate cost/testimony branches as already stated.

### Additional adversarial tests

- confused-contract matrix across sandbox, Keyword Overview paid probe, and this adapter;
- operator-deny cases including uppercase forms, `cache:`, `definition:`, `related:`, and
  `-site:`, plus a natural-language false-positive control such as `website comparison`;
- keyword empty/81-character/11-word/leading-or-trailing-space/disallowed-character cases;
- one-shot isolation proving Keyword Overview paid-probe Evidence does not block this adapter;
- sandbox and Keyword Overview inspection/capability objects are refused by this adapter and
  this adapter's objects are refused by their paths;
- fixture and Keyword Overview Derivations skip this Evidence-only adapter.

## Implementation report

**Parent:** `34c083474b4e1fbf8d0c3b84ab0eb210476e0976`
**Child:** `7608d7cd4fd37492b2471518be1aefcdfccaa2b6`
**Status:** `review`
**PF-10 only:** yes. Nothing pushed.

### Changed paths

- `src/observatory/capture_event.py` (third exact HTTP-v2 branch)
- `src/observatory/dataforseo_google_organic_paid_probe.py` (new)
- `tests/test_dataforseo_google_organic_paid_probe.py` (new)
- this ticket (Start commit, Status, Implementation report)

### Adapter token

`dataforseo-serp-google-organic-live-advanced-paid-probe-v1`

### Deterministic vector

Fixed inputs: keyword `observatory test`, nonce `5555…55`,
`authorized_at=2026-08-18T20:00:00.000000Z`,
`observatory_version=conformance-google-organic-paid-probe-v1`.

| Artifact | Value |
|---|---|
| request body (179 bytes) | `[{"depth":100,"device":"desktop","group_organic_results":true,"keyword":"observatory test","language_code":"en","load_async_ai_overview":true,"location_code":2840,"os":"windows"}]` |
| request SHA-256 | `0ea1022be28baf54e8a68f49002c963ada85f78082dec843030db28458498e2b` |
| fingerprint | `9ab79d6031d2a82a9aec4d9c6c5399bd540fcbbea80fca8a0216911333cedb02` |
| Attempt ID | `b577bc1fb75f4ba7576a96c1328fbe74df9d975f3bd03f6c01d7441dfed1a1be` |
| sample complete Capture ID | `ab94c98e528e776317c459a2dc2f8010b33b8ce142bab52d4e699fb5599d41c4` |

### Public CLI and pre-Attempt gates

```
uv run python -m observatory.dataforseo_google_organic_paid_probe capture \
  --evidence-root PATH --keyword "…" --authorize-max-micro-usd 30000
uv run python -m observatory.dataforseo_google_organic_paid_probe inspect \
  --evidence-root PATH --capture-id 64_HEX
```

No public endpoint/timeout/limit/location/device/depth/headers/task JSON/alternate ceiling.
Gates before Attempt: exact int `30000`, closed keyword grammar + operator deny, one-shot
keyed on this adapter token (KO Evidence does not block), loopback-only internal override
`http://127.0.0.1:<port>/v3/serp/google/organic/live/advanced`.

### PF-09 ownership inherited

Adapter owns URL resolution, headers, Authorization, timeout
`httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)`, ceiling `33_554_432`,
capability, spend, Capture. Shared seam only streams. Shared module still has no 32 MiB or
120s constants. Tests truncate with a 16-byte substitute bound.

### Existing conformance IDs unchanged

- sandbox Attempt `22adc4841c86b7cd98b90bba683aeac204a0cb568428b590fd399e8627eb4640`
- KO Attempt `89904bf8a6812fb3d0d845310e4705962bb4db928b80da3be67342dff5def185`
- existing `test_http_event_v2` / `test_dataforseo_paid_probe` / `test_dataforseo_sandbox`
  / `test_http_single_exchange` remain green

### Network I/O paths

The only send is `_exchange` → `perform_bounded_http_exchange` → `production_http_client`
when no test client is injected, targeting `https://api.dataforseo.com/v3/serp/google/organic/live/advanced`.
Public `capture_*` and CLI capture use that path. Inspect performs no I/O. Ordinary tests
autouse-block `socket.create_connection` except `127.0.0.1`/`::1`, inject `MockTransport`,
and delete credential env vars. No live probe was run.

### Isolation evidence

Confused-contract validators; sandbox/KO capabilities cannot execute this `_exchange` and
this capability cannot execute theirs; used capability is one-exchange; inspect refuses
sandbox, KO, partial, no-response, and tamper; fixture and KO derive write no rows for this
adapter; one-shot ignores existing KO Attempts.

### Weakest part / unguessed ambiguity

The adapter gate is a close clone of the KO paid probe (deliberate isolation, will drift).
Operator deny is conservative substring match (`fluid:` would fail). I did not guess
provider max response size, whether 120s is enough for depth-100 + async AIO, rank meaning
of `group_organic_results=true`, or current Live price vs the $0.002 snapshot. Live send
remains separately gated.

### Checks

`uv run pytest -q`: 845 passed, 1 skipped  
`uv run ruff check .`: clean  
`uv run mypy`: clean

Review vs `34c0834`: added inspect KO/no-response/tamper, credential-echo, successful
loopback, and mixed-store KO Evidence. Residual: local type name
`GoogleOrganicPaidProbeOutcome` follows the KO `PaidProbeOutcome` pattern and is not the
domain Outcome.

### Unproven

No TLS, real timeout, provider behavior, F6, F7, or live spend.

## Steward implementation acceptance

The Project Steward independently reviewed implementation commit
`7608d7cd4fd37492b2471518be1aefcdfccaa2b6` against exact start commit
`34c083474b4e1fbf8d0c3b84ab0eb210476e0976` and accepts the zero-network implementation.

Verified:

- clean `main` at the implementation commit;
- exact four-path scope: event-v2 closed-adapter validation, the new PF-10 adapter, its
  dedicated tests, and this ticket;
- exact closed request/policy/keyword grammar and deterministic request/fingerprint/Attempt
  vectors;
- exact 30,000 micro-USD acknowledgement and adapter-keyed one-shot guard before Attempt;
- committed/read-back-verified Attempt before the only send-capable path;
- PF-09 shared exchange with PF-10-owned 32 MiB response ceiling and 30/120/30/30 timeout;
- no public endpoint, timeout, response ceiling, provider-option, header, or alternate-spend
  control; the small response-bound override is confined to the internal deterministic test
  path;
- sandbox, Keyword Overview, and PF-10 adapter/capability/inspection isolation;
- existing sandbox and Keyword Overview conformance identities remain green;
- Evidence-only behavior; fixture and Keyword Overview Derivations skip this adapter;
- no live provider, DNS, credential, or spend activity during review;
- `uv run pytest -q`: `845 passed, 1 skipped`;
- `uv run ruff check .`: clean;
- `uv run mypy`: clean.

This is **implementation acceptance, not PF-10 closure and not live-call authorization**.
PF-10 remains `review` until the ticket's live closure gate is separately satisfied: fresh
official contract/pricing review, retention/privacy/provider-terms/API-redistribution
acceptance, bounded F6 off-host protection acceptance, explicit [CHAZ] one-shot authorization,
the resulting Evidence inspection/scrub/protection/restore proof, and final Steward closure.
