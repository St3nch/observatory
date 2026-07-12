# The Observatory — Post-M13 / Pre-M14 Deep Audit

Status: advisory audit report — not doctrine, not an owner decision, not schema/implementation/provider-spend/roadmap authority
Auditor: Claude (fresh repo-first session; no reliance on prior project summaries)
Date: 2026-07-12
Directive: `planning-inbox/claude-post-m13-deep-audit-directive.md` (read in full)
Repo audited: `https://github.com/St3nch/observatory.git` @ `2c60b4ca8fa0861343ced3089e741b8ff039f3aa` ("Close M13 and prepare post-M13 Claude audit")

---

## 1. Executive Verdict

The Observatory since the M7-era audit has done something most planning-heavy projects never manage: it converted doctrine into executable enforcement and then survived contact with reality. The single M13 live probe was executed exactly as governed — one request, one task, $0.002 reconciled across three cost witnesses, zero retries, a preserved 401 incident instead of a silent retry, and a hash-locked purge on schedule. The M12 C2 slice, the hammer matrix, the decision chain, and the fail-closed posture are all real and mutually consistent at the level of intent.

However, the repo as committed today contains one serious gap and a cluster of authority-drift problems:

**The paid-execution path is still armed in committed source.** `LIVE_EXECUTION_AUTHORIZED = True` is hard-coded, the owner-confirmation "gate" is a string constant committed next to the code that checks it, and the only duplicate/spend memory is a git-ignored file that exists on exactly one machine. On any fresh clone with credentials in the environment, one CLI command sends a second paid C00 request — directly contradicting the accepted closure ruling "No additional provider request authorized." Nothing in the repo's enforcement layer encodes the fact that M13 is closed. The safety cage worked during M13 because the owner was careful; it does not currently work because the code makes it work.

Second, the repo's own front door lies about what phase it is in. `README.md` and `LLM_START_HERE.md` still say M7; `ROADMAP.md` and `NEXT_SESSION_HANDOFF.md` still say M13 is active; only `ACTIVE_CONTEXT.md` says M14. All five carry the label "authority." A fresh session following the mandatory read order ingests three conflicting phase statements before reaching the correct one.

Third, the entire M8–M13 chain was closed against **draft** contracts, while `contracts/README.md` states "Only `accepted` binds." That is a quiet structural contradiction M14 should not inherit.

None of this changes the verdict that the underlying architecture is sound and unusually well-governed. The verdict is:

**CONDITIONAL GO for M14 planning** — conditions in §18. M14 *implementation* (even a bounded prototype) should not begin until the live path is disarmed and the sanitized M13 evidence is committed.

---

## Compact Findings Table

| ID | Sev | Conf | Category | Finding (short) |
|---|---|---|---|---|
| F-01 | **Critical** | proven (code) | Spend/authority integrity | Live paid-execution path remains armed post-closure; confirmation phrase is a committed constant; duplicate protection is machine-local only |
| F-02 | **High** | proven | Evidence preservation | Accepted M13 evidence (packages, attempt registry, purge proof) exists only on one machine in a git-ignored folder; no sanitized artifact committed despite the decision allowing it |
| F-03 | **High** | proven | Doctrine/code contradiction | `core.py` "permanent fixture-only guard" + `pyproject` `network="disabled"` + `__init__` docstring contradict `live_execution.py`'s enabled path, which bypasses core's guard entirely |
| F-04 | **High** | proven | Stale authority | README (M7), LLM_START_HERE (M7), ROADMAP (M13 active), NEXT_SESSION_HANDOFF (M13 active) conflict with ACTIVE_CONTEXT (M14 active); all labeled "authority" |
| F-05 | Medium | proven | Provider control gap | Post-receipt cost stop condition (decision-mandated) not implemented; cumulative campaign/stage budget checks exist but are not wired into the execution path |
| F-06 | Medium | proven | Provider control gap | Attempt-registry lifecycle not closed in code: records are written as `reserved_before_transport` and never updated; the 401 incident record that gates replacement authority was maintained out-of-band; no file locking |
| F-07 | Medium | proven | Evidence completeness | Live preflight snapshot is computed then discarded; evidence package numbering skips `01-*`; the durable package never records the preflight state that authorized the send |
| F-08 | Medium | proven | Authority drift | All 13 M7 contracts remain `draft`; M10–M13 closures treated them as binding, contradicting contracts/README rules 2 and 4 |
| F-09 | Medium | proven | Research lineage gap | RG3/RG8 named Kaizen Hermes intake docs as required inputs (M5 plan) but never consumed them; the gap is untracked |
| F-10 | Medium | open design question | M14 sequencing | OR-D1–OR-D4 (auth model, raw-pointer exposure, evidence withdrawal, update-window feeds) all open while M14 is active; tracker not refreshed at M13 closure |
| F-11 | Medium | likely defect (as proof) | Fixture false confidence | H4/H5 "rejection" is substring marker matching — demonstrative, trivially bypassable; H19/H21/H22 proven only over in-memory frozen dataclasses; must not be cited as proof for M14 surfaces |
| F-12 | Low | proven | Drift-tooling inconsistency | Two incompatible field-path fingerprint variants (`[i]` vs `[]`, 25-item truncation undocumented in output) — cross-probe drift comparison will silently mislead |
| F-13 | Low | proven | Hygiene | Test-evidence docs record 13/67/105 tests; current suite is 131 (verified passing in this audit's clean clone); latest count unrecorded. planning-inbox/README numbering duplicated (two "3", two "6") |
| F-14 | Low | proven | Dead scaffolding | Consumed one-time replacement mechanism (phrase, incident probe ID) remains a live code branch |
| O-1..O-10 | Opportunity | — | Capability/commercial | See §12–§13 |

---

## 2. Repo State Verified

```text
Remote:      https://github.com/St3nch/observatory.git
Branch:      main (origin/HEAD -> origin/main)
HEAD:        2c60b4ca8fa0861343ced3089e741b8ff039f3aa
Commit:      Sun Jul 12 11:33:51 2026 -0400  "Close M13 and prepare post-M13 Claude audit"
Working tree: clean; in sync with origin
Audit clone: performed in the auditor's sandbox from the live remote (the auditor
             cannot run git on the owner's Windows machine; content is identical —
             owner should confirm C:\dev\observatory is at the same HEAD)
Inventory:   ~140 files, ~48.7k lines; src/ (2 packages, 6 modules), tests/ (5 suites)
Test run:    python3 -m unittest discover -s tests → Ran 131 tests, OK
             (executed in this audit's sandbox; all provider transports mocked;
             no network calls, no provider spend, no repo modification)
```

No provider calls were made, no schema was created, no repository file was modified.

---

## 3. What Changed Since the M7-Era Audit

The M7-era audits (`audits/full-repo-audit-2026-07-07.md`, `audits/m7-audit-report-2026-07-07.md`) reviewed a documents-only repo. Since then:

- **M7** closed with all 13 non-schema contracts drafted and indexed.
- **M8** produced the H1–H22 hammer matrix and acceptance-gate policy, with OR-B1–B3 explicitly carried open under fail-closed defaults.
- **M9** accepted C2 (Controlled Public Manual Observation Package) as the first slice, with per-hammer applicability named.
- **M10** produced a logical (non-DDL) schema plan for C2 with recorded defaults (panel deferred, raw optional-but-first-class, internal evidence identity only, six minimum audit events).
- **M11** accepted foundation expectations only (no files created — a discipline worth noting).
- **M12** built and locally proved the C2 spine: `src/observatory_c2/c2.py` + `tests/test_c2_first_slice.py`, fixture-based, stdlib-only, in-memory.
- **M13** produced the largest artifact set in the repo: a proposed-then-accepted controlled probe decision, an accepted $50 staged exploratory-campaign decision with per-pull confirmation gates, a fixture-only CLI safety cage, a campaign recipe catalog (C00–C07, only C00 promoted), 42-case hostile-path planning, official verification records, authenticated pricing evidence, a usage-sheet reconciliation spec, one live C00 pull, a preserved 401 incident, a one-time authorized replacement, a reviewed evidence package, exact three-witness cost reconciliation, and a hash-locked raw purge — then closed with M14 activated for planning only.

The project also grew real code-level safety machinery: immutable recipe dataclasses, request-hash duplicate keys, preflight blocker vocabularies, evidence-root path containment, atomic tmp-file writes, credential redaction, and Decimal-based cost math. This is a materially different project from the one audited at M7, and mostly a better one.

---

## 4. Project Doctrine As Actually Implemented

The doctrine — telescope/astronomer, testimony-not-truth, fail-closed rights/retention, promote-out, typed-reads-only — is not merely restated; it is visibly encoded:

- **Observation vs. meaning:** C2 rejects strategy-marker text in `operator_intent` and `observed_text`; the M10 plan explicitly excludes strategy/recommendation/truth-score families; the read-tool skeleton forbids `store_recommendation` and names the fake-mustache variants.
- **Testimony:** every recipe carries a `claim_use_warning`; the C00 review explicitly refused to promote any field to schema; the closure decision records DataForSEO as "narrowly validated for the exact C00 SERP recipe," not admitted.
- **Fail-closed:** every gate in `build_preflight`/`build_live_preflight` accumulates named blockers; unknown scope/rights/retention classes reject; the hammer vocabulary correctly refuses to count `blocked_*` as pass.
- **Promote-out:** consumer-promotion and overlay contracts exist as drafts; nothing interpretive is persisted anywhere in `src/`.

Where doctrine and implementation diverge is not in what the code *stores* (nothing) but in what the code *permits* (F-01/F-03) and in what the authority documents *claim* (F-04/F-08). The database has not become the astronomer. The risk right now is different: the safety cage's disarm switch lives in prose (decisions) while the arm switch lives in code, and the two are no longer synchronized.

---

## 5. Strongest Parts of the Current System

Worth naming explicitly, because the correction sequence should not damage them:

1. **The decision-record discipline.** Every milestone transition has a dated, scoped, non-authorization-bounded decision file with anti-drift notes. The M13 probe decision's proposed-vs-accepted separation and its "no fake-mustache interpretation" clause are genuinely unusual quality.
2. **The incident handling.** The 401 placeholder-credential incident was preserved as evidence, a replacement was separately and explicitly authorized with its own confirmation phrase, and the replacement was single-use with registry-verified incident preconditions. Most projects would have silently retried. This is the single strongest proof that the governance culture is real.
3. **Three-witness cost reconciliation** using `max()` (conservative) rather than averaging — the cost model mirrors the provider-disagreement doctrine.
4. **The immutable recipe catalog.** Frozen dataclasses, deterministic serialization, request SHA-256 in the duplicate key, `validate_catalog()` asserting that only C00 is promoted — this is the right shape for every future provider.
5. **The C00 review's restraint.** "This complexity is evidence against designing a physical schema from one payload" is exactly the correct conclusion from a 162-path sample, and the field triage (provenance candidates / volatile-optional / raw-support-first) is a ready-made M10-v2 input.
6. **The hammer result vocabulary** — `blocked_not_implemented` is not pass — plus the honest per-milestone caveating ("accepted only for the bounded local C2 fixture implementation") prevented the classic fixture-theater failure at the *documentation* level. (§9 covers where it still exists at the *proof* level.)
7. **The read-tool skeleton** already contains most of what M14 needs: status-aware evidence lookup, forbidden request types, coverage/blind-spot output, `consumer_promotion_required`, overlay no-storage fields.

---

## 6. Critical and High-Severity Findings

### F-01 — The paid-execution path is armed in committed source (Critical)

**Files:** `src/observatory_dataforseo_probe/live_execution.py` (constants `LIVE_EXECUTION_AUTHORIZED = True`, `OWNER_CONFIRMATION_PHRASE`, `REPLACEMENT_CONFIRMATION_PHRASE`, `ATTEMPT_REGISTRY_PATH`), `cli.py` (`live-execute`), `.gitignore` (`probe-evidence/`), vs. `decisions/2026-07-12-m13-closure-and-m14-activation.md` ("No additional provider request authorized").

**What is wrong.** The gate that decides whether a paid request may be sent is composed of: (a) a hard-coded `True`; (b) a confirmation phrase committed two lines above the code that compares against it, passable as `--owner-confirmation` by any process; (c) two self-asserted booleans (`--account-limits-recorded`, `--evidence-root-ignored`) that the code trusts without verification, even though the git-ignore claim is trivially machine-checkable; and (d) a duplicate registry at `probe-evidence/dataforseo/attempt-registry.json` — a path that is git-ignored and therefore **empty on every clone except the owner's machine**. On a fresh clone with `DATAFORSEO_LOGIN`/`DATAFORSEO_PASSWORD` in the environment, `duplicate_attempt_exists()` returns `False` and the exact sequence M13 closed as consumed is repeatable.

**Why it matters.** The Observatory's entire spend-control claim is that authority lives in accepted decisions and the code enforces them. Right now the code enforces the *July 12 morning* authority state (one request permitted), not the *July 12 evening* state (zero requests permitted). The exposure is small in dollars ($0.002 per accidental C00) but the pattern is the thing: as the campaign catalog grows to C05 ($1.00 ceilings) and beyond, "the disarm lives in prose" becomes real money, and it also fails the project's own H7/H17 doctrine — an LLM agent with repo access and env credentials can read the confirmation phrase and satisfy every gate programmatically. A confirmation phrase committed beside its verifier is not a human-approval gate; it is a comment.

**Failure scenario.** Owner (or a future agent session with ob-dev access and env credentials) re-clones or works from a second machine; runs `live-execute` to "check the preflight behavior"; registry is absent; request fires; a second $0.002 task appears; worse, the pattern is normalized and repeated for later, costlier recipes.

**Correction.** (1) Flip `LIVE_EXECUTION_AUTHORIZED` to `False` in the next commit, with the closure decision as the cited reason — this is the one-line disarm. (2) Longer-term, derive execution authority from data, not a constant: a small committed `provider-authority.json` (decision path + recipe_id + remaining-authorized-request-count, normally 0) that the preflight reads, so that arming requires a visible commit tied to a decision. (3) Replace per-request confirmation phrases with values that are *not* committed (e.g., the owner supplies the preflight's freshly generated request-hash back, or an interactive confirmation) so an agent cannot self-satisfy the gate from repo contents. (4) Verify `evidence_root_ignored` via `git check-ignore` instead of a flag. (5) Commit a sanitized attempt/spend ledger (see F-02) so duplicate protection survives clones.

**Gate:** Blocks any future provider work and should be fixed before M14 prototype work begins (a prototype session with tools is exactly the confused-agent scenario). Does not block M14 *contract planning* on paper, but fix it first anyway — it is a 15-minute change.

### F-02 — Accepted M13 evidence is unpreserved outside one machine (High)

**Files:** `.gitignore` (`probe-evidence/`), `planning-inbox/m13-c00-post-pull-review-2026-07-12.md`, `decisions/2026-07-11-...` raw rules ("a sanitized manifest and sanitized field summary may be proposed for Git only after human review... it is not automatic").

**What is wrong / missing proof.** The durable products of M13 — request manifest, response summary, field inventory (the 162 paths and their set hash), item-type summary, cost reconciliation, purge proof, attempt registry with the preserved incident — live only in a git-ignored directory on `C:\dev\observatory`. The repo contains their hashes and counts transcribed into markdown, but not the sanitized artifacts themselves. The probe decision explicitly contemplated committing sanitized manifests after review; that step never happened. This matters three ways: (a) the M13 closure evidence is a disk failure away from being testimony-about-evidence rather than evidence; (b) F-01's duplicate protection has no cross-machine substrate; (c) M14 read-tool design wants the actual 162-path field inventory as its primary shape input, and right now no fresh session can read it.

**Correction.** Owner-reviewed commit of: `04-field-inventory.json`, `05-item-type-summary.json`, `06-cost-reconciliation.json`, `00-request-manifest.json`, `08-purge-proof.json`, and a sanitized attempt-registry snapshot, into a committed location (e.g., `providers/dataforseo/evidence/2026-07-12_C00.../` or `audits/`-adjacent). None of these contain raw result content or credentials by construction; the review the decision required is a short one. **Gate:** should precede M14 read-contract drafting (it is M14's best real-world input) and must precede any future probe (registry continuity).

### F-03 — Contradictory safety claims across code and config (High)

**Files:** `src/observatory_dataforseo_probe/core.py` (`NETWORK_EXECUTION_AUTHORIZED = False`; `execute_request` docstring "Permanent fixture-only guard until a later owner ruling"), `__init__.py` docstring ("Network execution is intentionally unavailable"), `pyproject.toml` (`network = "disabled"`, `provider_execution = "disabled"`), vs. `live_execution.py` (`LIVE_EXECUTION_AUTHORIZED = True`, full transport implementation that never touches core's guard).

**What is wrong.** The original fixture-only cage and the later live path coexist as parallel systems with opposite authority constants. `core.execute_request` is now a decorative guard: the live path imports around it. A maintainer, auditor, or LLM reading `core.py`, the package docstring, or `pyproject.toml` would conclude network execution is impossible — which is false. This is precisely the "stale statement treated as current" failure mode the directive warns about, inside the enforcement layer itself.

**Correction.** Collapse to one authority source (the F-01 data-driven authority record); update or delete `core.execute_request` and the `__init__`/pyproject claims to describe the real state; keep the original C00-only fixture module clearly labeled as superseded scaffolding or remove it. **Gate:** with F-01; blocks later provider work.

### F-04 — Root authority files disagree about the current phase (High)

**Files/claims:** `README.md` ("Current status: M7"), `LLM_START_HERE.md` ("The current phase is M7 core contract planning" + M7-era do-not-start list), `ROADMAP.md` (milestone table row: M13 active, M14 planned; §M13 "Status: active"; §M14 "Status: planned"), `NEXT_SESSION_HANDOFF.md` ("Last updated: 2026-07-10... Active milestone: M13"), vs. `ACTIVE_CONTEXT.md` ("Last updated: 2026-07-12... M14 typed read API / MCP contract planning").

**Why it matters.** All five are labeled `authority`, and the mandatory read order puts three stale statements *before* the current one. The project's whole LLM-first premise is that a fresh session can trust the read path. Right now a rule-following fresh session would either stop confused or, worse, obey LLM_START_HERE's M7-era non-implementation rule and refuse legitimate M14 work — or obey the M13 handoff and try to restart provider-admission planning. Additionally, the M13 closure decision (unlike M7's, which had a follow-up table naming exactly these files) contains **no follow-up work table**, which is likely why the update was missed — a process regression worth noting on its own.

**Correction.** One maintenance commit updating README status line, LLM_START_HERE's "Current Non-Implementation Rule" (make it point at ACTIVE_CONTEXT instead of hard-coding a phase — this bug will otherwise recur every milestone), ROADMAP table + M13/M14 section statuses + an M13 closure progress-log entry, and NEXT_SESSION_HANDOFF. Restore the follow-up table convention in future closure decisions. **Gate:** blocks nothing mechanically; fix before the next fresh session.

---

## 7. Medium and Low Findings

### F-05 — Post-receipt stop conditions and campaign-budget enforcement not wired in (Medium)

The accepted probe decision requires stopping after response receipt "if provider-reported cost exceeds $0.10." `execute_one_c00` parses the payload, writes the evidence package, and records reconciliation status (`review_required` on mismatch) — but takes no action on a cost overrun and enforces no ceiling post-receipt. Similarly, `validate_batch` and `conservative_spend` correctly encode calibration/batch/campaign ceilings, but nothing in the execution path consults cumulative campaign spend before sending. For a single reconciled $0.002 pull this was harmless; for the remaining ~$48 of campaign authority it is the difference between "budget enforced" and "budget audited afterward." **Proven defect vs. spec (the decision's stop condition), not vs. observed behavior.** Correction: before any next pull, the execution path must (a) read the committed spend ledger, (b) enforce stage + campaign remaining budget pre-send, (c) hard-fail (with incident record) on post-receipt cost > ceiling. Blocks later provider work.

### F-06 — Attempt-registry lifecycle is open-ended and hand-maintained (Medium)

`reserve_attempt` writes `status: reserved_before_transport`; no code path ever updates the record on success, transport failure, or provider error. Yet `replacement_attempt_allowed` gates on records having `status: provider_authentication_error`, `http_status: 401`, `retry_permitted: false` — fields no code writes. The preserved incident record was therefore edited out-of-band, meaning the registry that gates replacement authority is partially hand-authored JSON in a git-ignored folder. Also: registry updates are read-modify-write with no locking — correctly caveated in the closure review as "pass for one-operator probe path" (H20), but it must be fixed before batch mode. Correction: close the lifecycle in code (reserve → transported → classified outcome written back atomically), and treat any registry record lacking a terminal status as a stop condition. Blocks later provider work / batch mode.

### F-07 — The authorizing preflight is not part of the durable evidence package (Medium)

`execute_one_c00` builds the live preflight, checks it, and discards it. The package numbering (`00, 02, 03, 04, 05, 06, 07, 08`) visibly reserves `01` for it, and the M13 preflight-record template exists, but the tool never writes `01-live-preflight.json`. The evidence package therefore proves what happened but not what state authorized it to happen. Correction: persist the preflight snapshot (it already contains no secrets — `credential_values_recorded: False` by design) as `01-*` in the package. Blocks later provider work; also a good pattern for M14 read-audit events.

### F-08 — The contract layer was never accepted, and everything downstream leaned on it anyway (Medium, cheap to fix, high leverage)

Every one of the 13 M7 contracts still reads `Status: draft` (verified by header grep). `contracts/README.md` rule 2: "Only `accepted` binds." Rule 4: "M10 plans schema from **accepted** contracts." M10, M12, and M13 closures all cite the contract *draft set* as their behavioral basis. This is not a behavioral defect — the drafts were honored — but it is exactly the kind of authority ambiguity the repo's own rules exist to prevent, and M14 is about to draft the real read-tool contract as a child of an unaccepted skeleton whose parents are unaccepted. Correction: an explicit owner decision either (a) accepting the contract set as v0.1 (possibly with per-contract carve-outs for open OR items, which the contracts already mark), or (b) recording that draft contracts bind provisionally under a named rule. Option (a) is better; the contracts were reviewed, consumed, and survived M8–M13 contact. Should precede M14 contract drafting.

### F-09 — RG3/RG8 named research inputs were never consumed, and the gap is untracked (Medium)

`research/m5-research-gate-plan.md` names "Kaizen Hermes evidence/intake docs" as inputs to RG3 (evidence-ID/citation) and RG8 (claim-safety report language); `planning-inbox/repo-first-research-triage.md` names the specific kaizen-docs packet files (442–447). Neither `rg3-...md` nor `rg8-...md` contains any reference to them (verified by grep), and no tracker row, review note, or research doc records the omission. Since RG3 → `evidence-id-citation.md` → the M14 evidence-handle design, and RG8 → `claim-safety.md` → M14 claim-use metadata, this is the one research-lineage gap that lands directly on the active milestone. Correction: either consume the named Kaizen Hermes intake docs as a bounded M14 planning input (they reportedly contain claim-to-evidence linking precedent) or record an explicit "not consumed, reason, accepted" note in the tracker. Does not block M14 planning start; should be resolved before the evidence-handle contract is drafted.

### F-10 — Group D owner rulings are all open with M14 active; tracker not refreshed at closure (Medium)

`planning-inbox/owner-ruling-tracker.md`: OR-D1 (consumer auth/authz model), OR-D2 (raw-pointer exposure outside internal tools), OR-D3 (withdrawal/deprecation/supersession finalization), OR-D4 (update-window feeds) — all open, all labeled "needed before M14 API/MCP." That is fine for *planning* (M14 can and should draft the ruling proposals), but the tracker was also not updated at M13 closure: OR-C2 (long-term raw retention posture) remains correctly open, but there is no C-group annotation recording that the C00 pull executed under the accepted capture-and-purge posture, and no D-group note that M14 is now the active consumer of those rulings. Correction: refresh tracker; make OR-D1–D4 explicit early M14 deliverables (proposal → owner decision) rather than discoveries at prototype time. Blocks M14 *implementation*, not planning.

### F-11 — Fixture-proof boundaries: know exactly what H4/H5/H19/H21/H22 evidence is worth (Medium as a proof-scope note; the documentation already caveats it)

The C2 strategy/customer rejection (H4/H5) is substring matching against ~10 markers (`"recommend "`, `"customer_email="`, ...). "You should really go after the term X" or a customer email in any normal format sails through. As a *demonstration that the envelope has a rejection concept*, fine; as *protection*, essentially none — and M14 must not cite it as strategy-rejection proof for read outputs. H19 append-only is proven only by Python `frozen=True` dataclasses; H21 audit-first by tuples returned from pure functions; H22 recovery by a JSON digest of an in-memory object. All of these semantics evaporate the moment a persistence substrate exists. The closure documents caveat this correctly ("accepted only for the bounded local C2 fixture implementation") — this finding exists so the caveat is not eroded by repetition. Correction: none now; M14/M-persistence hammer plans must re-derive these from scratch against the real substrate, and the eventual customer/strategy rejection needs a design better than marker strings (structural field allow-lists + classification review, not blocklists). 

### F-12 — Two incompatible shape-fingerprint variants (Low/Medium for H13)

`core.shape_fingerprint` emits indexed list paths (`$[0].x`) truncated at 25 items; `evidence_package._field_paths` emits collapsed paths (`$.items[]...`) also truncated at 25, sectioned differently. The accepted "162 normalized field paths" is the evidence-package variant. Cross-probe drift comparison (H13's whole point) requires one canonical fingerprint; the truncation limit should also appear *in the output* so a 30-item SERP is not silently fingerprinted as a 25-item one. Correction: standardize on the collapsed-path variant, record `list_truncation_limit` in the artifact, retire or rename the core variant. Feeds M14 drift-warning design; fix before the next probe.

### F-13 — Minor hygiene (Low)

(a) Test-evidence docs record 13 → 67 → 105 tests; the committed suite is now 131 (this audit executed it: `Ran 131 tests, OK`) — record the current count with the commit hash. (b) `planning-inbox/README.md` reading-order numbering has two "3" and two "6" entries. (c) `update_campaign_index` silently replaces entries sharing a `probe_id` — acceptable for an operational index, but note it is not append-only and should never be cited as evidence of record.

### F-14 — Retire the consumed replacement mechanism (Low)

The one-time replacement path did **not** create a reusable loophole — on the owner's machine it is consumed (a `replacement_for` record blocks a second), and on a fresh clone the replacement branch fails closed (`replacement_incident_not_present`); the fresh-clone exposure is entirely the *normal* path (F-01). But `REPLACEMENT_CONFIRMATION_PHRASE` and `REPLACEMENT_INCIDENT_PROBE_ID` remain live branches in committed code for an event that is over. Dead authorization scaffolding accumulates into exactly the ambiguity F-03 describes. Correction: remove the branch (the incident stays preserved in the registry/ledger); if a future incident occurs, mint a new, incident-specific mechanism then.

---

## 8. M8 Hammer Audit

**Overall:** H1–H22 is a strong, well-sourced matrix; the result vocabulary and the "blocked ≠ pass" rule are its best features, and the milestone gate mapping gave M9–M13 real teeth. Specific critique:

**Weak or under-specified hammers.**
- **H5/H4 as content tests are under-specified adversarially.** The matrix says "test hidden strategy in notes / operator_intent / nested payloads" but never demands a bypass corpus. Given F-11, add explicit adversarial cases: paraphrased recommendations, strategy expressed as questions, customer identifiers in nonstandard formats, unicode/homoglyph evasion, strategy in raw-payload fields. More fundamentally, decide whether content-based rejection is even the right mechanism (structural allow-lists are stronger) and write the hammer against the mechanism actually chosen.
- **H13 lacks a fingerprint-identity requirement.** It demands drift detection but never requires a single canonical fingerprint algorithm with recorded parameters — F-12 slipped through exactly this gap. Add: "two payloads compared for drift must be fingerprinted by the same versioned algorithm; algorithm version and truncation parameters are part of the artifact."
- **H7 assumes the enforcement point but never tests its *state provenance*.** The matrix tests "paid capture without approval rejected" but not "approval state must be derived from committed decision-linked data, survive a fresh clone, and be un-forgeable by an agent reading the repo." F-01 is the live counterexample. Add a hammer case: fresh-clone environment + credentials + repo-derivable confirmation strings must NOT be sufficient to send a paid request.
- **H21 audit-first cannot be meaningfully tested pre-persistence** — currently "proven" over returned tuples. Mark it explicitly `blocked_not_implemented` for any surface without a transaction boundary, so the M12 acceptance language stops implying more than it is.

**Missing hammers (mostly M14-relevant; the directive's list, checked against the matrix):**
- **Evidence-handle guessing/enumeration** — nothing tests that `ev_*` IDs are non-sequential/non-enumerable and that a guessed handle returns a uniform not-found (no existence oracle across scopes). Add to H15/H17.
- **Pagination abuse / filter explosion / result ceilings** — H18 covers malformed input; nothing covers *well-formed* exhaustive extraction (page-walking an entire scope, wildcard filters). M14 needs explicit ceilings-and-refusal hammers.
- **Misleading LLM context assembly** — nothing tests that an evidence pack cannot be assembled in a way that drops mandatory caveats (e.g., requesting fields à la carte and omitting `claim_use_warning`). Required warnings must be non-detachable from the payloads they qualify; hammer it.
- **Prompt-injection via stored observation content** — observed text (titles, PAA questions, snapshots) is attacker-controlled web content that will be fed to LLMs at read time. No hammer covers "observation content containing instructions must be delivered as inert data (typed/enveloped), never interpolated into tool guidance." This is arguably the most important missing hammer for M14.
- **Stale-read/purge race at the read layer** — H20 covers write races; add: a read concurrent with purge/supersession must never return a payload whose status metadata says one thing while content says another.
- **Semantic drift** (provider changes a field's *meaning* without changing shape) — acknowledged nowhere as testable; at minimum require provider-doc version capture per pull so semantic drift is investigable.
- **Rights downgrade over time** — H2 tests admission-time rights; nothing tests "rights_class changes after admission → dependent evidence transitions to blocked_by_rights and read tools honor it."

**Can the hammer system actually stop dangerous implementation?** At the planning layer, yes — M9–M13 demonstrably shaped work around it. At the enforcement layer, only partially: hammer *results* live in prose reviews, not in a machine-checkable ledger, and nothing prevents a milestone from closing with a hammer quietly unexecuted except steward diligence. A small committed `hammer-results` register (hammer ID → surface → commit → result → evidence path) would convert the gate from cultural to structural. Recommend as an M14 deliverable.

---

## 9. M9–M12 Implementation Audit

**Does the C2 slice prove the right things?** Mostly yes, for what it claims. The spine — envelope validation, fail-closed scope/rights/retention, candidate/admitted separation, evidence-identity minting, supersession-as-new-record, hash-verified raw manifest, deterministic recovery digest — is the correct skeleton, and the ID layering (observation_id ≠ evidence_id ≠ raw_support_id, citation handle derived) matches `evidence-id-citation.md`. The 13-test suite exercises real rejection paths, and `validate_no_external_markers` is a cute structural tripwire.

**False confidence risks** (beyond F-11): the slice proves *validation logic*, not *storage semantics*. There is no store at all — no uniqueness, no append-only enforcement point, no transaction, no concurrent admission surface — so H1/H19/H21 evidence is about function purity, not isolation. The M12 closure language handled this honestly; the risk is future documents citing "H19 passed at M12" without the fixture qualifier. Treat every C2 hammer as re-openable at first persistence.

**Gaps between contracts and code:** `capturepackage-v0-1.md` requires approval-reference and cost-ceiling fields "when paid" — C2 has no paid path, fine; but C2's envelope also lacks the contract's `provider_or_capture_instrument` field (it has `capture_method` only) — harmless now, worth aligning before schema planning v2. Freshness is proven only as "a point-in-time warning string must exist," which is the thinnest possible H9 — no freshness *status computation* exists anywhere yet; M14's freshness metadata will be designed against a contract that has never been exercised.

**Choices that will help or hurt M14+:** Frozen dataclasses, deterministic JSON, and the tuple-of-issues validation pattern will translate cleanly. Two things will hurt: (a) `evidence_id`/`observation_id` are bare `uuid4().hex` with no scope or family component and no registry — fine in-memory, but the ID-minting contract for persistence (collision domain, resolvability, non-enumerability) is undesigned; (b) `citation_handle = f"cite:{evidence_id}"` bakes OR-A4 (still open) into a format; keep it visibly provisional. No premature abstraction found — the code is admirably small.

---

## 10. M13 Provider-Probe Audit

**Did the probe prove the intended gates?** Yes, within its declared bounds, and the boundary honesty is exemplary. Specific assessments per the directive:

- **Credential handling:** good — env-only, redaction of secret values in error text, `credential_values_recorded: False`, basic-auth built at send time. One gap: `redact_text` only masks values present in env at call time; an HTTPError body is truncated to 500 chars and redacted, but headers of the outbound request never enter evidence, which is correct. No credential found in any committed artifact. Pass.
- **Spend controls:** per-request controls real and proven; **cumulative and post-receipt controls are prose-only (F-05)**. The $0.10 ceiling was enforced pre-send via exact-price match ($0.002) — note this preflight actually enforces *price equality* to the expected price, which is stricter than the ceiling and a nice touch.
- **Duplicate prevention:** the design (provider+endpoint+payload-hash+approval-ref, reserve-before-transport, failure leaves the reservation in place blocking retry) is correct and was proven by the incident itself. Its substrate is machine-local (F-01/F-02).
- **Incident handling:** the strongest part of M13 — see §5. The replacement mechanism's preconditions (`incident_ok and not replacement_already_recorded`) were exactly right; it created **no reusable loophole** (F-14 analysis), only dead scaffolding to retire.
- **Evidence packaging:** complete and well-shaped, minus the preflight snapshot (F-07). Cost reconciliation with three witnesses and conservative `max()` is better than the decision required.
- **Raw retention & purge:** the purge ran seven days *early* (captured 14:59 UTC, purged 15:20 UTC same day — "sooner after the owner accepts the field summary" honored), with pre-purge hash, byte count, path-containment check, and idempotence guard (`purge proof already exists` blocks). Pass, and durable proof language matches the artifact. Do not weaken this pattern.
- **Provider attribution:** every artifact carries `provider_testimony_only_not_truth` or a recipe-specific claim warning; the field review refused promotion. Pass.
- **The 162-field result — implications:** (a) *Parser:* a depth-10 organic query already produced 4 item families and deep optional nesting; parser design must be per-item-family with an explicit unknown-family quarantine (the code's `unknown` counting is the right seed). (b) *Drift:* the field-path-set SHA-256 is the correct drift primitive, but only under one canonical fingerprint (F-12) and only once ≥2 samples exist per recipe — C01 (mobile) is the natural next drift pair *when separately authorized*. (c) *Read-tool design:* the field triage in the post-pull review (provenance candidates / volatile-optional / raw-support-first) should be promoted into a committed provider field-classification note; M14's evidence-pack shape should serve the first class, caveat the second, and *never* pass the third through a read tool.
- **Did sanitized evidence retain enough structure after purge?** Yes for M14 planning purposes (inventory + item-type summary + cost + statuses), **provided it gets committed (F-02)**. One real loss to note honestly: with raw purged, no future question about *values* (e.g., "what did a PAA expanded element actually look like") can be answered from evidence — only from a new authorized sample. That is the accepted trade of capture-and-purge, but OR-C2 (durable retention posture per family) should be decided before the campaign resumes, because purging every calibration payload makes the campaign's learning partially unrepeatable.
- **Harden before any future distinct probe:** F-01, F-02, F-05, F-06, F-07, F-12 — in that order.

---

## 11. M14 Planning Requirements

What M14 must get right, stated as requirements (no implementation implied). The typed-read-tool skeleton already covers ~60% of this; items marked ★ are not yet in it.

1. **Typed read surfaces.** Start from the skeleton's nine request types; for the prototype, cut to four: `evidence_lookup`, `panel_evidence_pack` (or its C2-era equivalent: package/observation listing per scope), `freshness_check`, `coverage_blind_spot_read`. Everything else waits for its owning milestone (cross-check→M16, overlay→M17).
2. **Query/filter boundaries.** Closed filter vocabulary per request type (scope, family, time window, evidence status, provider). ★ No free-text filters, no regex, no field projection that can drop mandatory caveat fields (caveats must be structurally non-detachable).
3. **Scope & authorization.** One caller = one scope grant set; scope must be asserted in every request and echoed in every response; cross-scope requests fail closed (H1). OR-D1 must be *proposed* early in M14 — recommended shape: static per-consumer credential class (kaizen / neon_ronin / searchclarity / internal_llm) with per-scope allow-lists, no self-service scope expansion. ★ Uniform not-found: a handle outside the caller's scopes must be indistinguishable from a nonexistent handle.
4. **Evidence handles vs. provider IDs vs. raw pointers.** Only `evidence_id`/citation handles cross the boundary. Provider task IDs appear solely inside provider-attribution blocks, labeled. Raw pointers never appear (OR-D2 default: internal-only) — responses may carry `raw_support_status` (exists/purged/blocked) but never a path. ★ Handles must be non-enumerable (random component) and status-aware on resolution (skeleton R4's six statuses).
5. **Pagination & ceilings.** ★ Hard max page size, hard max total results per request, opaque cursors bound to the original filter set (no cursor replay with widened filters), and a per-caller read-rate budget — reads are cheap but context-flooding and scrape-shaped extraction are still failure modes.
6. **Freshness/staleness caveats.** Every pack: `captured_at`, computed `freshness_status`, `volatility_class` (even if the initial vocabulary is just `unknown_volatility` — honesty over invention), and claim-fitness per the freshness contract. Stale + `current_state` claim intent → block or degrade to historical with warning (H9, OR-B3 fail-closed default).
7. **Provider attribution & disagreement.** Attribution block mandatory on any provider-derived value; multi-provider responses return per-provider series side by side; no averaging, no winner fields (H8). Disagreement summaries are compute-on-read output only (OR-A1 fail-closed).
8. **Claim-safety metadata.** `claim_intent` required on request; response carries `claim_status` + warnings from `claim-safety.md`; recommendation/report/prediction/causality intents → reject or evidence-only + `consumer_promotion_required` (skeleton R11/R14).
9. **Rights & retention visibility.** `rights_class`/`retention_class` on every pack; `blocked_by_rights`/`expired_by_retention` evidence never returned as active; ★ a rights change after admission must propagate to reads (the rights-downgrade hammer from §8).
10. **Redaction.** Field-level allow-list per caller class (define the visibility matrix in the contract, not in code); customer/private markers in any outbound field are a hard error, not a filter.
11. **Tool descriptions / guidance metadata.** ★ Tool descriptions themselves are a security surface: they must state the testimony/caveat semantics, must not promise recommendations, and — critically — retrieved observation *content* must be delivered in a typed data envelope the guidance explicitly marks as untrusted third-party web content (the prompt-injection hammer from §8).
12. **LLM-context assembly.** Evidence packs should be assembly-ready: stable IDs inline with each datum, caveats adjacent to the values they qualify (not in a detachable footer), blind-spot section last, and a declared token-budget behavior (truncate by dropping whole observations with a `truncated: true` flag — never by dropping caveats).
13. **Error taxonomy.** Deterministic, enumerable error codes in the `blocked_*` house style; errors must not leak existence, scope names, counts, or paths.
14. **Audit events.** The skeleton says read paths create no events (V9's "no read events"); ★ M14 must reconcile this with H17/authorization needs — recommended proposal: no per-read *evidence* events (preserving V9), but an access log outside the evidence store for authz failures and ceiling breaches. Needs an explicit ruling either way.
15. **Rate/cost protections for reads** — covered in (5); note reads must also never trigger capture or spend (skeleton R9) including via "recapture_required" outputs, which are advisory strings only.
16. **Confused/malicious-agent resistance.** ★ Acceptance tests must include: agent replays tool descriptions as instructions; agent requests SQL-shaped strings inside legal filters; agent walks handles; agent asks for "everything in scope"; observation content containing "ignore previous instructions"; request smuggling recommendation-storage under `evidence_lookup` free-text fields (answer: there are no free-text fields).
17. **Determinism.** Same request against same evidence state → byte-identical response (modulo generated_at); required for hammer reproducibility and citation stability.
18. **Prototype acceptance criteria.** Fixture-backed (C2 objects + the committed C00 sanitized inventory as the two evidence families), local-only, no network, no DB, all applicable hammers (H1, H5, H8, H9, H10, H15, H16, H17, H18 + the new ones from §8) executed with recorded results, and the F-01-class test: nothing in the repo suffices to authorize a write or a spend through the read layer.
19. **Must remain deferred:** production deployment, any real MCP endpoint exposure, Postgres/schema/migrations, auth *implementation* beyond the contract, overlay handling, report-safe references (OR-A4/M15), cross-check persistence (OR-A1/M16), any new provider request.

**Owner rulings M14 needs sequenced early:** OR-D1 (auth model), OR-D2 (raw pointer — recommend accepting the internal-only default as a ruling), OR-D3 (withdrawal/supersession read behavior), OR-A4 scope-down (internal citation handles only for M14), plus the read-audit question in (14).

---

## 12. Dangerous-Capability Opportunities

## How The Observatory Could Become Unusually Powerful Without Becoming The Strategy Engine

The moat thesis in `strategy-layer-dangerous-design.md` is correct and worth restating in evidence terms: **the defensible asset is the longitudinal, provenance-complete, rights-clean observation corpus plus the joins nobody else preserves — not the LLM, not the provider.** Everything below stores only observations; interpretation stays compute-on-read; anything accepted promotes out. Classification: value / prerequisites / rights risk / cost risk / technical risk / milestone fit.

**O-1. Multi-provider disagreement maps (SERP first).** Same panel query captured via ≥2 providers/engines; store both testimonies; read tools return side-by-side series with incomparability warnings. *Value:* very high — "here is where the tools disagree, with receipts" is a product no subscription tool sells, and it operationalizes the project's core doctrine. *Prereqs:* M16, OR-A1 stays compute-on-read, second provider or second engine (C02 Bing is already in the catalog). *Rights:* low (provider API terms already reviewed for DataForSEO; each added provider needs its own admission). *Cost:* low (pennies per comparison pair). *Tech:* medium (metric-identity mapping — RG9 groundwork exists). *Fit:* M16.

**O-2. SERP feature evolution & volatility evidence.** Per panel run, record item-family composition (the item-type summary already computes it) and diff across runs: feature appearance/disappearance, rank churn, domain-diversity shifts. Mechanical Tier-2 derivations only. *Value:* high — grounds the freshness/volatility vocabulary in measurement instead of folklore (deep-research lane R4), and volatility classes are load-bearing for every claim-safety output. *Prereqs:* recurring or at least repeated capture (OR-C11 / M18) and panel contract activation. *Rights:* low. *Cost:* the main lever — cadence math needed first (lane R3). *Tech:* low. *Fit:* M18 planning; earliest data from repeated authorized calibration pulls.

**O-3. AI-citation / GEO surface comparison ("citation asymmetry").** Store per-surface, per-prompt, per-date mention/citation observations (DataForSEO AI Optimization as the ruled canonical source; C05 AI Mode is already catalogued); read-time joins expose "surface X cites competitor pages of type Y for query class Z; the subject is absent." *Value:* highest strategic value in the portfolio — GEO measurement science is young (lane R1) and honest, sampled, caveated citation evidence is rare; directly powers SearchClarity's most differentiated report section. *Prereqs:* OR-C3 (AI Optimization admission), AI-surface family design (V18/K6 — distinct families, never collapsed), sampling-threshold rulings (OR-E3). *Rights:* medium — provider-mediated (good), but claim-safety language is critical (H10). *Cost:* medium ($10 stage S4 already budgeted for shape learning). *Tech:* medium-high (volatility of generated answers demands repeated sampling before any absence claim). *Fit:* shape evidence in remaining M13-style campaigns (separately authorized), families at next schema planning, proof at M15/M16 era.

**O-4. Entity/source recurrence across answer engines.** Cross-surface Tier-2 mechanical rollup: which domains/entities recur in AI citations across surfaces and dates within a scope. Pure counting over stored observations — passes the materialization test if kept mechanical and recomputable. *Value:* high (the "who does AI trust in this vertical" evidence, stated safely as observed recurrence). *Prereqs:* O-3 first. *Rights:* low. *Cost:* zero marginal. *Tech:* entity normalization is the hard part — keep it at domain level first. *Fit:* after O-3.

**O-5. Public-page change lineage (snapshot family).** Point-in-time snapshots of public pages (the register already blesses snapshots and kills the content graph), hash-chained per URL, with mechanical diff summaries. *Value:* high — "the page that took the ranking changed X on date Y" is evidence competitors almost never preserve; also feeds intervention alignment (NC3) without storing interventions. *Prereqs:* capture-instrument admission (deferred family; Firecrawl is fallback-only per V23; rights review per source), storage posture (V12 blob+hash), OR-C4 archive layout. *Rights:* **medium-high — the honest hard part**; per-source review, robots/ToS posture, retention rules. *Cost:* low-medium. *Tech:* medium. *Fit:* dedicated future family drill-in; do not smuggle into M14.

**O-6. Marketplace visibility evidence at the compliant ceiling.** Manual, human-captured point-in-time public observations (Etsy/Fiverr per the RG7 ceilings), through the slim manual-capture family (V16), with brutal point-in-time caveats (S3). *Value:* medium-high commercially (SearchClarity's marketplace clients) precisely because compliant longitudinal marketplace evidence is scarce. *Prereqs:* OR-C5/C6/C7/C8 rulings; manual-capture family contract. *Rights:* the defining constraint — the ceiling is the product. *Cost:* human time, not dollars. *Tech:* low. *Fit:* post-M15 planning.

**O-7. Query-panel intelligence + coverage/blind-spot + cost-to-close (NC5+NC7 join).** Panels as versioned measurement programs; blind-spot output that states unobserved surfaces *with the provider price to observe them* attached as metadata. *Value:* high — turns "what don't we know" into a costed decision input for the owner without the Observatory ever recommending anything (the read output states cost facts; the astronomer decides). *Prereqs:* panel contract activation (deferred at M10), provider price table as observed provider metadata. *Rights/cost/tech:* low. *Fit:* M14 can design the blind-spot output shape now; pricing metadata later.

**O-8. Historical observation replay / "as-of" reads.** Read tools accept `as_of` and reconstruct what the Observatory knew at a past date (append-only + supersession make this nearly free if designed in now). *Value:* medium-high — retroactive analysis, dispute resolution, and "we saw it first" proof; brutal to retrofit. *Prereqs:* OR-D3 supersession semantics; persistence design. *Fit:* design into M14 contract (a request field), implement at persistence.

**O-9. Freshness-aware LLM context packs.** The evidence-pack format itself as a product: caveats-inline, blind-spots-last, token-budget-declared packs any strong LLM can consume safely. *Value:* medium alone, multiplier on everything else — this is what makes the astronomer dangerous. *Fit:* this **is** M14; treat pack ergonomics as a first-class deliverable, not a serialization detail.

**O-10. Low-cost sentinel campaigns & rare-SERP-feature capture.** Tiny standing budgets that fire one authorized observation when a volatility spike or a rare feature (new AI block type, new item family) is detected in normal panel runs, preserving specimens of transient SERP features. *Value:* medium-high and genuinely rare (nobody preserves dead SERP features; longitudinal feature archaeology compounds). *Prereqs:* recurring capture governance (M18), automated-trigger spend rules — the hardest governance ask here; keep human-approved until the F-01-class controls are structural. *Fit:* M18+.

**Anti-opportunity note:** several lanes (O-2, O-4, O-7) produce Tier-2 mechanical derivations. Each must pass the V6 materialization test explicitly and be recomputable-from-observations, or it is VEDA Brain growing a mustache. The test is cheap; run it per derivation, in writing.

---

## 13. Commercial Leverage and Consumer-Boundary Analysis

**Can the planned system support profitable work without contaminating the core?** Yes — the promote-out architecture is not just doctrinally clean, it is commercially *correct*: every deliverable lives in the consumer that bills for it, while the evidence corpus stays reusable across all of them (Kaizen K2's separation of observation from requester is the enabling design).

- **SearchClarity (nearest revenue).** Products: evidence-cited SEO/GEO audits, AI-citation asymmetry reports (O-3/O-4), before/after proof sections via overlay alignment (NC9, no storage), marketplace visibility snapshots at the compliant ceiling (O-6). What it needs from Observatory: panel evidence packs, citation-handle→report-safe-reference mapping (OR-A4/OR-E1, M15), freshness/claim-status metadata so report language self-polices, disagreement output (OR-E4). What stays in SearchClarity: customers, engagements, report text, action plans, consent, first-party analytics. The differentiator worth leading with commercially is O-3: honest, sampled, dated AI-surface evidence with safe language — the market is currently served folklore.
- **Neon Ronin.** Workspace-scoped read grants + a pull-*request* queue (request recorded as consumer job metadata, never autonomous spend) matches its own external-integration contract. Needs from Observatory: scope-mapped evidence packs and blind-spot output so workspaces can *ask* for coverage.
- **Kaizen.** Cites evidence IDs in decisions/returns; needs stable, durable handle resolution (O-8's as-of reads make governance citations robust forever) — a strong argument for designing handle permanence into M14.
- **Internal evidence products.** market_watch scopes + O-7 costed blind-spots + eventually O-10 sentinels = the owner's own gap-hunting substrate; monetization is downstream (new niches, new SearchClarity offerings), never in-database.
- **High-value observations competitors fail to preserve** — the shortlist to prioritize: (1) dated AI-citation samples per surface, (2) SERP item-family composition over time (not just rank), (3) provider disagreement pairs, (4) transient/dead SERP feature specimens, (5) rights-clean marketplace point-in-time observations. These five compound with time and are the corpus's actual moat.
- **Boundary risks to watch commercially:** report deadlines are the classic pressure that pushes conclusions into the evidence store ("just cache the summary"). The existing forbidden-pattern lists anticipate this; the M15 hammer set (H4/H16) is where it must be proven, and the O-2/O-4 materialization tests are where it will be tempted first.

---

## 14. Project Hygiene and Stale-Authority Findings

Consolidated (details in §6–7): F-04 (README/LLM_START_HERE/ROADMAP/NEXT_SESSION_HANDOFF phase conflicts — the top hygiene item, with the root cause being the missing follow-up table in the M13 closure decision); F-03 (pyproject/`__init__`/core claims contradict live code); F-08 (contract statuses never advanced); F-10 (owner-ruling tracker not refreshed at M13 closure); F-09 (untracked RG3/RG8 input gap); F-13 (test-count evidence lag; planning-inbox README numbering). Additional small items: `archive/CLAUDE_START_HERE.md` is properly archived (good); the directive's required-read list names `planning-inbox/research/research-review-summary.md`, which exists and reads as reconciled — no unapplied-patch markers found in it; `REPO_MAP.md`'s planned `providers/` folder is now earned in spirit by M13 and would be the natural home for the committed C00 sanitized evidence (F-02) plus the DataForSEO field-classification note (§10) — creating it should be a recorded ruling per the folder-gate rule, and is recommended.

A structural suggestion: milestone closures currently require editing five root files by hand. Consider making ACTIVE_CONTEXT the *single* phase authority and demoting the phase statements in README/LLM_START_HERE/handoff to pointers ("see ACTIVE_CONTEXT for current phase") — this class of drift then becomes impossible rather than merely checked.

---

## 15. Recommended Correction Sequence (dependency-aware)

```text
Step 1  (safety, no dependencies, ~1 line + tests)
        F-01a: LIVE_EXECUTION_AUTHORIZED → False, citing the M13 closure decision.
        F-14:  remove the consumed replacement branch in the same pass.

Step 2  (evidence preservation; enables Step 3; needs owner review of sanitized files)
        F-02:  commit sanitized C00 package artifacts + attempt-registry snapshot
               (recommended home: earn providers/ per REPO_MAP gate, via a small decision).

Step 3  (structural spend authority; depends on Step 2's committed ledger)
        F-01b: authority-from-data (committed decision-linked authority record,
               registry continuity, git-check-ignore verification,
               non-committed confirmation values).
        F-03:  reconcile core.py / __init__ / pyproject claims to the new single source.

Step 4  (authority hygiene; independent, do immediately after Step 1)
        F-04:  refresh README / LLM_START_HERE / ROADMAP / NEXT_SESSION_HANDOFF;
               make phase statements pointers to ACTIVE_CONTEXT;
               restore follow-up tables in closure decisions.
        F-13:  record current test count (131 @ 2c60b4c); fix inbox numbering.

Step 5  (contract authority; before M14 read-contract drafting)
        F-08:  owner decision accepting the M7 contract set as v0.1
               (with open-OR carve-outs as already marked in each contract).
        F-10:  refresh owner-ruling tracker; schedule OR-D1–D4 as early M14
               proposal→ruling deliverables.
        F-09:  consume or explicitly waive the Kaizen Hermes RG3/RG8 inputs.

Step 6  (probe-tooling hardening; blocks the NEXT provider pull, not M14 planning)
        F-05:  wire post-receipt cost stop + cumulative stage/campaign budget
               into the execution path, reading the committed ledger.
        F-06:  close the attempt-registry lifecycle in code; treat non-terminal
               records as stop conditions; add locking before batch mode.
        F-07:  persist the live preflight as 01-* in the evidence package.
        F-12:  one canonical shape fingerprint, truncation recorded in output.

Step 7  (hammer system upgrades; fold into M14 hammer planning)
        §8 additions: fresh-clone spend hammer, handle enumeration, pagination/
        extraction ceilings, non-detachable caveats, stored-content prompt
        injection, rights downgrade, purge/read race; plus a committed
        machine-readable hammer-results register.
```

---

## 16. Owner Decisions Required

1. **Disarm ratification** — confirm `LIVE_EXECUTION_AUTHORIZED=False` and the authority-from-data direction (Steps 1/3).
2. **Sanitized-evidence commit** — review and approve the C00 artifacts for Git, and rule on earning `providers/` (Step 2 / F-02).
3. **Contract-set acceptance** — accept the 13 M7 contracts as v0.1 or record a provisional-binding rule (F-08).
4. **OR-D1** consumer auth/authz model (proposal to be drafted in M14).
5. **OR-D2** — recommend ruling the existing default (raw pointers internal-only) into a decision.
6. **OR-D3** withdrawal/supersession read behavior; **OR-A4 scope-down** (internal citation handles only for M14).
7. **Read-audit posture** — reconcile "no read events" (V9) with access-logging needs (§11.14).
8. **OR-C2** — durable-vs-purge retention posture per source family, *before* the exploratory campaign resumes (purging every calibration payload trades away repeatability).
9. **Hammer-results register** — approve the committed machine-readable register as an M14 deliverable (§8).
10. **RG3/RG8 Hermes inputs** — consume or waive (F-09).

---

## 17. What Must Remain Deferred

Unchanged from the M14 activation decision, restated so this report cannot be cited otherwise: Postgres creation, physical schema, migrations, live provider ingestion, **any additional paid provider request** (including the remaining ~$48 of campaign envelope — it is budget authority, not execution authority), bulk/recurring capture, customer data and customer first-party analytics storage, direct SQL or DB credentials for LLMs/agents, production API/MCP deployment, public exposure, dashboards, customer-facing reports, strategy/recommendation storage, automatic conclusion promotion, marketplace scraping, browser-extension capture, Ahrefs/Semrush work, cross-scope aggregation (OR-G1), and every killed ancestor concept. The opportunity classifications in §12 are analysis, not roadmap changes.

---

## What I Would Want Before Trusting This With Expensive, High-Value Visibility Evidence

If I were the astronomer about to depend on this telescope for evidence that money and reputation ride on, I would want, in order:

1. **Spend and capture authority encoded as committed, decision-linked data** — not constants, not phrases readable from the repo, not machine-local files. Until F-01/F-03 are fixed, the system's honesty depends on the operator's memory, which is exactly what the project was built to not depend on.
2. **Evidence that survives the machine.** Committed sanitized manifests, a durable attempt/spend ledger, and (at persistence time) tested restore with hash verification (H22 for real). Today the accepted M13 evidence would not survive one disk failure.
3. **One authority voice per fact.** Phase in one file, contract bindingness in one status field, execution authority in one record — with every other document pointing rather than restating (F-04/F-08).
4. **Hammers with a machine-readable ledger and adversarial teeth** — especially the fresh-clone spend test, non-detachable caveats, stored-content injection, and handle enumeration — so "the hammers passed" is a checkable claim tied to commits, not a sentence in a review.
5. **A real freshness/volatility vocabulary grounded in ≥2 samples per class** before any output labels evidence "fresh," and repeated sampling before any absence claim on AI surfaces. One payload proved shape; only repetition proves stability, and the claim-safety layer is only as honest as the volatility data under it.
6. **Rejection mechanisms stronger than substring markers** for the strategy/customer boundaries, because the day the corpus is valuable is the day someone is tempted to cache a conclusion in it.
7. **A parser with an unknown-quarantine and one canonical drift fingerprint**, so the first silent provider shape change becomes a warning, not corrupted evidence.

The encouraging part: every item on this list is a hardening of something the project already believes and mostly already documents. Nothing requires a doctrine change. The telescope's optics are good; the observatory just needs its doors to lock from the inside of the decisions, not the inside of the source file.

---

## 18. Final Recommendation

**CONDITIONAL GO for M14 planning.**

M14 contract/planning work may proceed immediately. Conditions, by gate:

- **Before any M14 prototype implementation session (hard):** F-01 Step-1 disarm committed; F-04 authority refresh committed (a tools-equipped prototype session reading today's repo is the exact confused-agent scenario the boundaries warn about).
- **Before M14 read-contract acceptance (hard):** F-02 sanitized C00 evidence committed (it is the primary real-world shape input); F-08 contract-set acceptance decision recorded; OR-D1/D2/D3 proposals drafted and ruled or explicitly fail-closed in the contract text.
- **Before any future provider request (hard, independent of M14):** F-01b/F-03 structural authority, F-05, F-06, F-07, F-12, and an OR-C2 retention ruling.

No finding here requires reopening M13: the probe itself was executed lawfully and reviewed honestly, and its closure stands on its own evidence. The findings are about what the closed milestone left armed, unpreserved, or unstated — all correctable in days, all cheaper to fix now than after M14 gives this repo its first door that opens outward.

---

*This report is advisory source material only. Per the directive and `audits/README.md`, it is not accepted doctrine, an owner decision, schema approval, implementation approval, provider admission or spend approval, M14 prototype approval, roadmap authority, or permission to modify the repository. Any document citing this audit as authority for a capability is invalid by construction.*
