# The Observatory — Post-v1 / Pre-Database Deep Audit

Status: advisory audit report — not doctrine, not an owner ruling, not schema/migration/database-creation/provider/implementation/production authority
Auditor: Claude (fresh repo-first session; prior post-M13 audit and its full remediation trail read and reconciled)
Date: 2026-07-12
Directive: `planning-inbox` post-v1 / pre-database audit directive (read in full)
Repo audited: `https://github.com/St3nch/observatory.git` @ `aa65747357e4a374f811da2af23aba6059215750` ("Accept Observatory v1 and close M20")

---

## 1. Executive Verdict

Between the post-M13 audit and v1 acceptance — apparently in a single extraordinary day — the project executed seven milestones, and it did so with the same discipline the prior audit praised and with a remediation response that is close to a model of how to consume an adversarial audit: every one of the fourteen prior findings has a verifiable disposition, the live paid path is disarmed in committed source, the sanitized C00 evidence survives the machine, the contract layer was formally accepted, ten owner rulings were closed with real decisions, and every proof artifact now carries proof-class/execution-surface/proof-strength labels that make overstatement structurally harder.

The accepted v1 is what it says it is: a bounded, local, fixture-backed proof of the governed evidence architecture, honestly labeled, with a known-limits register that is unusually candid. My independent verification confirms the core claims — a clean clone runs 184/184 tests, the disarm is real, the committed evidence matches the recorded hashes, and the acceptance language does not overstate the proof.

**Final v1 verdict: PASS WITH REQUIRED CORRECTIONS** (§20, §27). The corrections are documentation-truth defects, not proof defects — most visibly, `README.md` and `LLM_START_HERE.md` still assert that "M14 is active," a direct recurrence of the prior audit's F-04 that survived seven milestone closures because the pointer-not-restatement fix was only half applied.

**Database-phase verdict: CONDITIONAL GO for physical planning** (§21, §28). Nothing doctrinal blocks planning. What blocks the *later* gates is concrete and nameable: the hammer authority layer is still `draft` with OR-B1/OR-B2 unruled — meaning "hammer tests are a hard gate" has, seven closed milestones later, no accepted definition of what constitutes the gate; there is no consolidated logical data contract (the M10 plan covers only C2, while M14–M17 minted a much richer concept vocabulary that exists only in per-contract prose and fixture code); the clone-stable, decision-linked enforcement substrate for spend/duplicate/authority deferred from F-01 still does not exist; OR-C2 and OR-C4 (retention posture and raw archive layout) remain open and directly block raw-support physical design; and the fixture suite — for the first time — contains a demonstrable false-confidence example: the typed-read extraction ceiling silently hides evidence beyond `MAX_TOTAL_RESULTS` with `truncated: false`, a defect the fixtures can never trigger because no fixture scope exceeds the ceiling. I proved it by adding units in a sandbox (§12, N-01).

None of these are reasons to stop. All of them are reasons the first migration must not be authorized until a data-contract freeze, an accepted hammer-gate policy, and a database hammer harness exist.

---

## Compact Findings Table (new findings this audit)

| ID | Sev | Conf | Classification | Category | Finding (short) |
|---|---|---|---|---|---|
| N-01 | **High** | proven defect (demonstrated) | fixture false confidence | Typed-read | `MAX_TOTAL_RESULTS` silently drops evidence beyond the ceiling with `truncated: false, omitted: 0`; contract §15 omits the disclosure requirement the M14 requirements package accepted; fixtures never exceed the ceiling, so 184 green tests cannot see it |
| N-02 | **High** | proven | open owner ruling / authority drift | Hammer authority | `hammer-matrix-v0-1.md` and `acceptance-gate-policy-v0-1.md` remain `Status: draft`; OR-B1/OR-B2 open since M8; v1 accepted "hammer tests are a hard gate" with no accepted definition of the gate; no per-hammer (H1–H22) result ledger exists — registers are suite-level only |
| N-03 | **High** | missing proof / future requirement | Logical schema | No consolidated logical data contract: M10's plan covers C2 only; M14–M17 concepts (evidence unit, caller grant, cross-check side, disagreement read model, overlay window, report-safe reference) live in scattered contract prose and fixture dataclasses; physical design currently has no single frozen input |
| N-04 | **High** | accepted limitation → pre-ingestion blocker | Enforcement substrate | Clone-stable, decision-linked spend/duplicate/authority enforcement (F-01 structural remainder + F-05/F-06/F-07) still absent; committed sanitized ledger is preservation-only — no code consults it |
| N-05 | Medium | proven defect | Authority drift (F-04 regression) | `README.md` states "M14 ... is active"; `LLM_START_HERE.md` line 113 hard-codes "the active M14 planning boundary" two lines after its own rule forbidding hard-coded milestones; both stale across M15–M20 closures |
| N-06 | Medium | open owner ruling | Raw-support design | OR-C2 (retention posture per family) and OR-C4 (raw archive layout) open; both directly block physical design of raw-support/manifest persistence |
| N-07 | Medium | accepted limitation | Recovery | Encrypted/off-machine backup blocked (no owner tool/key path); acceptable for v1, unacceptable before real evidence enters Postgres |
| N-08 | Medium | likely defect (contract/prototype delta) | Typed-read | Contract §15 requires cursor expiration; prototype cursors carry no expiry and none is listed in the register's limitations |
| N-09 | Low | proven | Contract hygiene | Accepted `typed-read-api-mcp-v0-1.md` §24 still says Hermes lineage "not yet consumed"; it was consumed and resolved the same day (`m14-hermes-lineage-review-2026-07-12.md`); the accepted contract asserts a gap that no longer exists |
| N-10 | Low | likely defect (pattern) | Code | Mutable module-level fixture dicts (`EVIDENCE`, `GRANTS`) — I mutated them at runtime trivially; harmless in a read-only prototype, forbidden as a pattern for DB-backed repositories |
| N-11 | Low | likely defect (latent) | Authorization | `freshness_check` nests `evidence_lookup`, so authorization is checked against the nested request type; a caller granted `freshness_check` but not `evidence_lookup` would be wrongly blocked — no such grant exists in fixtures, so tests can't see it |
| N-12 | Low | future requirement | Secrets | HMAC cursor key is a hard-coded source constant; must become a managed secret with rotation posture before any DB-backed or network-exposed read |
| N-13 | Low | proven | Typed-read | `consumer_promotion_required` is hard-coded `False` — never computed; fixtures never approach promotion, so the contract behavior is unproven |
| N-14 | Low | likely defect (pattern) | Layer translation | M15 silently remaps `provider_metric_statement`/`ai_geo_sampled_observation` → `historical_observation` before calling M14; correct here, but undocumented claim-intent translation between layers is a semantic-drift channel to govern |
| O-1..O-8 | Opportunity | — | — | §25 |

---

## 2. Repository State Verified

```text
Remote:        https://github.com/St3nch/observatory.git
Branch:        main (origin/HEAD -> origin/main)
HEAD:          aa65747357e4a374f811da2af23aba6059215750
Commit:        Sun Jul 12 18:35:14 2026 -0400  "Accept Observatory v1 and close M20"
origin/main:   aa65747... (identical — synchronized)
Working tree:  clean
History:       132 commits; M14→M20 span 24 commits with a consistent
               draft → rulings → contract-accept → implement → record-proof → close cadence
Audit clone:   fresh clone from the live remote in the auditor's sandbox
               (owner should confirm C:\dev\observatory is at aa65747)
Test run:      python3 -m unittest discover -s tests → Ran 184 tests, OK
               (independently executed in this sandbox; no network, no provider calls,
                no secrets accessed, no repo modification, no destructive action)
Code markers:  zero TODO/FIXME/TBD/placeholder strings in src/ or tests/
```

---

## 3. Current Accepted-v1 State

`ACTIVE_CONTEXT.md` (authoritative, current): v1 accepted at the bounded proof-system ceiling; M0–M20 closed; **active milestone: none**; post-v1 implementation and production not authorized. `decisions/2026-07-12-observatory-v1-acceptance.md` records the exact owner phrase, the companion known-limits register acceptance, and a non-authorization list that covers every dangerous door. `ROADMAP.md` and `NEXT_SESSION_HANDOFF.md` are current. `README.md` and `LLM_START_HERE.md` are not (N-05).

## What The Accepted v1 Actually Proves

Stated precisely, with proof surfaces attached:

1. **The governance machine works under load.** Seven milestones, each with proposal → owner ruling → bounded authorization → implementation → recorded proof → closure, with zero authority shortcuts found in this audit. That cadence — not any single test — is v1's strongest proof.
2. **Contract-level fail-closed behavior is real, in code, across five packages.** Scope, rights, retention, freshness, claim-intent, private-data, recommendation, overlay-persistence, and provider-attribution rejections all execute and all have negative tests (184 passing, independently verified).
3. **A typed read boundary can serve caveated, provider-attributed, status-aware evidence packs** with per-caller scope/request grants, uniform not-found, HMAC-bound cursors, non-detachable warnings, untrusted-content labeling, and a prompt-injection fixture that stays inert (`ev_f19b6e40` carries "Ignore previous instructions..." as data).
4. **One real provider request can be governed end-to-end** — authorized, ceilinged, reconciled at $0.002 across witnesses, incident-preserving (the 401), purged with hash proof — and the sanitized evidence now survives the machine in `providers/dataforseo/evidence/`.
5. **Provider disagreement can be exposed without truth selection** — the M16 comparator classifies comparability, refuses winner/average logic structurally (forbidden request flags), and treats undefined proprietary metrics as `unresolved_incomparability`.
6. **Overlay values can be consumed and demonstrably not persisted at the code-path level**, with field manifests, forbidden-key rejection, and discard-status assertions.
7. **The repository itself is recoverable**: bundle → verify → restore → fsck → 184/184 on the restored tree, honestly classified as repository recovery, not database or disaster recovery.
8. **Overstatement resistance is now structural**: every result register carries `proof_class`, `execution_surface`, `proof_strength`, and explicit limitations.

## What The Accepted v1 Does Not Prove

The known-limits register already says most of this; the audit confirms and sharpens it:

1. **No storage semantics of any kind.** Every append-only, immutability, audit-first, uniqueness, transaction, isolation, rollback, and retention-transition claim is currently enforced by frozen dataclasses, call-site discipline, and the absence of a writer. There is no second writer, no concurrent reader, no migration, no long-lived datum. Every one of those invariants reopens at first persistence.
2. **No enforcement against a motivated or confused caller on a real surface.** Authorization is a dict lookup over fixture grants; cursors don't expire (N-08); rate budgets exist in prose, not code; the ceiling-disclosure defect (N-01) shows the fixture shapes were tuned to pass.
3. **No provider generality.** One endpoint, one request shape, one payload, one day. The 162-path inventory is a specimen, not a distribution.
4. **No memory-, log-, or infrastructure-level overlay safety** — code-path discard only, as M17 itself states.
5. **No hammer gate in the accepted sense.** OR-B1/OR-B2 open; the hammer matrix is draft; no per-hammer result exists (N-02). What v1 proves is a *test* gate, not the accepted *hammer* gate the doctrine names.
6. **No recovery of anything except the Git repository.** No database backup, no encrypted generation, no off-machine copy.

---

## 4. Prior Post-M13 Audit Reconciliation

The remediation trail (`post-m13-deep-audit-response-2026-07-12.md`, `post-m13-audit-final-reconciliation.md`) is complete, honest, and — unusually — refuses to fabricate retroactive evidence (e.g., declining to reconstruct the discarded C00 preflight timestamp, declining to expand disarmed code "merely to satisfy audit prose"). Finding-by-finding verification against the current tree:

| Prior ID | Prior sev | Prior concern | Remediation / proof files | Verified current evidence | Verdict | Database-phase implication |
|---|---|---|---|---|---|---|
| F-01 | Critical | Paid path armed; committed phrase; machine-local duplicate state | commit `241e90d`; response ledger | `LIVE_EXECUTION_AUTHORIZED = False` (live_execution.py:24) verified; confirmation phrase still committed but now gates nothing; structural authority-from-data **not built** | **partially resolved; remainder deferred with accepted fail-closed boundary** | Structural decision-linked, clone-stable authority is a hard gate before any ingestion (N-04) |
| F-02 | High | M13 evidence local-only | decision `2026-07-12-provider-evidence-folder-...`; commit `70482d8` | `providers/dataforseo/evidence/2026-07-12_C00_.../` contains manifest, summary, 162-path inventory (with declared normalization + 25-item truncation), item types, cost, purge proof, terminal sanitized ledger with preserved 401 incident | **fully resolved for preservation; unresolved for enforcement** — no code reads the committed ledger | Ledger must become the enforcement substrate, not a museum piece (N-04) |
| F-03 | High | Contradictory safety constants/claims | Batch A | pyproject: `network_implementation = "present_but_disarmed"`, `provider_execution = "disabled_after_m13_closure"`; core.py docstring now "Legacy fixture-only entry point; live transport exists elsewhere but is disarmed" | **fully resolved** | Single authority source still folds into the structural F-01 work |
| F-04 | High | Root files disagree on phase | Batch A | ROADMAP/handoff/ACTIVE_CONTEXT current, LLM_START_HERE gained the pointer rule (line 111) and drift-stop rule (line 125) — but README and LLM_START_HERE line 113 hard-code "M14 active" and went stale again through M15–M20 | **resolved, then regressed** (N-05) | Fix the restatements, not just the values, before a database roadmap adds more closures |
| F-05 | Medium | Post-receipt cost / cumulative budget not wired | response ledger | `validate_batch`/`conservative_spend` still not called by `execute_one_c00` — verified | **deferred with accepted fail-closed boundary** (code disarmed) | Hard gate before any future provider request/ingestion |
| F-06 | Medium | Attempt-registry lifecycle open; no locking | sanitized terminal ledger committed | lifecycle still open in code; disarmed | **deferred with accepted fail-closed boundary** | Same gate as F-05 |
| F-07 | Medium | Preflight not in evidence package | response ledger | accepted as future package field; historical artifact honestly not fabricated | **deferred appropriately** | Future provider package spec |
| F-08 | Medium | Contracts draft while relied upon | `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md` | all 13 contracts read `accepted — contract set v0.1`; four new v0.1 contracts individually accepted | **fully resolved** | — |
| F-09 | Medium | RG3/RG8 Hermes inputs unconsumed | disposition + `m14-hermes-lineage-review-2026-07-12.md` (SHA-256s of both Kaizen packets; principle-by-principle comparison; no conflict) | verified | **fully resolved** — except the accepted contract's §24 still asserts the gap (N-09) | Amend §24 in the next contract revision |
| F-10 | Medium | OR-D rulings open; tracker stale | M14 rulings decision | OR-D1–D6 all `ruled` in tracker with decision links; OR-C1 correctly annotated consumed | **fully resolved** | — |
| F-11 | Medium | Fixture false confidence; marker-based rejection weak | proof-classification note; hammers/README rule 10; result registers | proof-class labels adopted everywhere; M15/M17/M14 use structural allow-lists (field allow-lists, closed envelopes) as primary mechanism, markers supplemental | **substantially resolved at process level** — and immediately vindicated: N-01 is exactly the predicted class, caught only by adversarial probing outside fixture shapes | DB hammers must be adversarial-by-construction (§11) |
| F-12 | Low | Two fingerprint variants | committed inventory declares parameters | canonical single algorithm still unimplemented, correctly gated on "before any second payload" | **deferred appropriately** | Provider re-entry gate |
| F-13 | Low | Test evidence stale; index numbering | evidence notes; registers | current: 184 (verified); registers record 141/156/167/184 per milestone with commits | **fully resolved** | — |
| F-14 | Low | Consumed replacement scaffolding live | Batch A | zero `REPLACEMENT` references in live_execution.py; incident preserved in committed ledger | **fully resolved** | — |

**No prior finding was closed only on paper**; the two "partial" rows (F-01 structural, F-02 enforcement) are explicitly labeled as such in the project's own ledger — the wording and the risk match. **One regression** exists (F-04 → N-05). **One concern the prior audit under-specified** and this audit now proves: the fixture-false-confidence warning (F-11) was accepted procedurally but the *first shipped instance of it* (N-01) sailed through anyway, because process labels don't generate adversarial inputs — only adversarial tests do.

---

## 5. What Changed From M14 Through M20

- **M14**: contract-set v0.1 acceptance + OR-D1–D6 rulings + OR-A4 scope-down; the full 587-line `typed-read-api-mcp-v0-1.md` (26 sections covering callers, closed envelopes, claim intents, identity, status lifecycle, freshness, attribution, allow-lists, untrusted content, context assembly, ceilings, errors, logging, no-side-effect law, determinism, hostile paths, prototype boundary, proof metadata, deferrals); Hermes lineage consumed with hashes; a 399-line prototype (4 request types, 5 caller classes, HMAC cursors, uniform not-found, context packs with inline caveats); 141 tests; machine-readable result register (OR-D6 ruled and delivered).
- **M15**: SearchClarity proof-workflow contract v0.1 + OR-E1–E5 and OR-F1(M15-scope) rulings; a report-*support* layer (not report generation) that wraps M14 reads under `searchclarity_internal`, classifies dispositions (`supportable_with_caveats` / `historical_support_only` / `blocked`), maps internal handles to synthetic artifact-local report-safe references, and rejects customer/report/recommendation fields structurally; 156 tests.
- **M16**: provider cross-check contract v0.1 + **OR-A1 ruled: compute-on-read only** — the longest-open doctrinal question closed in the fail-closed direction; comparator with comparability classification, capture-distance seconds, disagreement typing, forbidden winner/average/composite flags; 167 tests.
- **M17**: overlay contract v0.1 + OR-F2/F3 (scope-bounded) rulings; synthetic overlay alignment with manifest allow-lists, forbidden identity/file keys, no-storage/discard assertions, temporal-alignment-only intervention timelines; a notable mid-milestone fix commit (`04ef29c` "Fix M17 cache safety test false positive") showing the false-positive vigilance is live; 184 tests.
- **M18**: recurring execution **rejected** for v1; a future policy accepted (cadence classes capped at weekly-candidate, per-run + rolling-30-day ceilings, no automatic retries/increases/fallbacks, duplicate keys binding scope+panel-version+recipe+window+shape-hash, mandatory review points); no scheduler artifacts of any kind — verified.
- **M19**: backup/restore rulings (protected unit, mode, timing, generations, restore proof, secret posture, cleanup posture); executed proof: bundle SHA-256 `c2b245d5...`, restored HEAD == source HEAD `fc7c69a`, fsck over 1067 objects, 184/184 on the restored tree, encryption honestly `blocked_pending_owner_tool_and_key_path`.
- **M20**: acceptance review recommending the exact bounded ceiling; known-limits register (eight proven-limit classes + full deferral list + preserved-artifact protection); owner acceptance with exact phrase; closure with no active milestone.

The cadence quality is uniform: every milestone has its own hostile-path plan, reconciliation review, ruling proposals, authorization decision, local test evidence, result register entry, and closure decision.

---

## 6. Strongest Parts of the System

1. **The audit-response discipline.** The response ledger's rule — "No item may be omitted because it is low severity, commercially oriented, long-term, inconvenient, or outside the active milestone" — was actually followed, and its refusals (no retroactive preflight fabrication, no expanding disarmed code to satisfy prose) are better evidence of integrity than compliance would have been.
2. **OR-A1 ruled compute-on-read.** The single decision most protective of the telescope/astronomer boundary at the database phase: no disagreement ledger, cache, or table without a later V6 materialization proof. The M16 comparator honors it — nothing is persisted.
3. **The layered consumer architecture.** M15 composes over M14 rather than reimplementing reads; `searchclarity_internal` gets a narrower grant than internal callers; report-safe references are synthetic, artifact-local, and separate from internal handles. This is exactly the shape a DB-backed consumer stack should keep.
4. **Proof-strength labeling as infrastructure.** `proof_class` / `execution_surface` / `proof_strength` / `limitations` on every register entry, plus hammers/README rule 10, makes it *hard* to launder a fixture pass into a persistence claim. The v1 acceptance language visibly benefited.
5. **The unresolved-incomparability posture in M16** — proprietary metric without a definition → `unresolved_incomparability`, not a caveat — encodes "provider disagreement is first-class evidence" more strongly than the contract required.
6. **The M18 rejection.** Declining to build recurrence, while writing the policy that will govern it, is the "not yet — earn it" stance functioning at v1's most tempting door.
7. **Honest recovery classification.** The M19 evidence explicitly lists what the restore proof is not — the exact opposite of the industry norm.

---

## 7. Critical and High Findings

No Critical findings. Nothing in the committed tree is armed, leaking, or misrepresenting proof in a way that endangers money, rights, or evidence today. The Highs are all pre-database blockers rather than present dangers.

### N-01 — The extraction ceiling silently hides evidence, and the fixtures cannot see it (High)

**Classification:** proven defect (demonstrated) + fixture false confidence + contract-language gap.
**Files:** `src/observatory_typed_read_prototype/reader.py` (`MAX_TOTAL_RESULTS = 4`; `units = units[:MAX_TOTAL_RESULTS]` before pagination; `omitted` computed against the post-slice list), `fixtures.py` (no scope exceeds 4 visible units), `contracts/typed-read-api-mcp-v0-1.md` §15.
**Prior-audit relationship:** the exact failure class F-11 warned about, and the class the M14 requirements package (R5/R12: "truncate by dropping whole observations with a `truncated: true` flag — never silently") accepted.

**What is wrong.** `observation_package_read` slices the visible unit list to the total-result ceiling *before* computing pagination and the omission count. Units beyond the ceiling are not merely withheld — their existence is denied: the final page reports `truncated: false, omitted_evidence_unit_count: 0`. I demonstrated it in a sandbox by adding units to scope B (7 visible): page 2 returned `truncated: False, omitted: 0` with 3 active evidence units invisible. Separately, contract §15 requires the ceiling but never requires *disclosure* of ceiling-hidden results — the contract text dropped a requirement the requirements package had accepted, and the prototype faithfully implements the weakened text. The 184-test suite is green because no fixture scope has more than 4 visible units.

**Why it matters.** An evidence system whose read layer can assert "you have seen everything" while withholding evidence violates the coverage/blind-spot doctrine (R8/NC5) at its own front door. At fixture scale it's cosmetic; against a real database with hundreds of observations per scope, every collection read becomes a silent partial view, and every absence-adjacent inference an LLM draws from it ("only 4 observations exist in this scope") is corrupted. This is also the audit's clearest exhibit that green suites over cooperative fixtures prove contract shape, not contract truth.

**Failure scenario.** DB-backed scope with 400 observations; consumer LLM pages through, receives 4 units and `truncated: false`; reports "the Observatory holds no other evidence for this scope"; a claim-safety-compliant report is assembled over a 1% sample presented as complete.

**Correction.** (1) Amend contract §15: any result withheld by any ceiling must be disclosed via `truncated: true` + accurate `omitted_evidence_unit_count` (or a `result_ceiling_reached` field) — never a clean final page. (2) Fix the prototype (compute omissions against the pre-ceiling visible count). (3) Add the adversarial test: a fixture scope larger than every ceiling, asserting disclosure on the final page. (4) Add this to the database hammer program as the canonical "silent partial view" hammer.
**Gates:** Blocks physical planning? No. Blocks migration implementation? No. **Blocks any database-backed read slice? Yes.** Blocks production? Yes.

### N-02 — The hammer authority layer is still draft, and v1's "hard gate" has no accepted definition (High)

**Classification:** open owner ruling + authority drift.
**Files:** `hammers/hammer-matrix-v0-1.md` (`Status: draft`), `hammers/acceptance-gate-policy-v0-1.md` (`Status: draft`), `planning-inbox/owner-ruling-tracker.md` (OR-B1 open, OR-B2 open, OR-B3 open), all M12–M17 closure decisions and `ACTIVE_CONTEXT.md` ("Hammer tests are a hard gate for implementation"), `test-results/*.json` (suite-level, not per-hammer).
**Prior-audit relationship:** prior §8 recommended a machine-readable hammer register; OR-D6 ruled it *allowed* and milestone registers exist — but they record suite passes, not H1–H22 statuses; the prior audit did not press on OR-B1/B2 remaining open, which this audit now must.

**What is wrong / missing.** The F-08 contract acceptance covered `contracts/` and the new v0.1 contracts — it did not touch `hammers/`. Seven milestones closed citing hammer coverage while the documents defining what a hammer pass means (OR-B1: acceptable mock/stub level) and which hammers hard-gate which milestone (OR-B2) remain unruled drafts. There is no committed artifact mapping H1–H22 → surface → result → commit. For v1 this was survivable because the acceptance honestly described a *test* posture. For the database phase it is disqualifying as-is: the phase's entire safety premise is "hammers must fail before we trust the database," and the project currently has no accepted rule for what failing/passing means, no accepted mapping of which hammers gate migrations, and no ledger to record them in.

**Correction.** Before any migration specification: (1) rule OR-B1 (recommended: fixture/mock passes never satisfy persistence-invariant acceptance; only real-substrate execution does — the draft's own default, promoted to ruling); (2) rule OR-B2 for the database phase specifically (which of H1–H22 + the §11 database hammers gate schema-spec acceptance, migration execution, first synthetic slice, first real observation); (3) accept a hammer-matrix v0.2 that absorbs the database hammer program; (4) extend the register format to per-hammer entries (`hammer_id`, surface, result vocabulary from the existing policy, commit, evidence path). OR-B3 can remain open (it gates M15-era report use, already fail-closed).
**Gates:** Blocks physical planning? No (planning can draft v0.2). **Blocks migration implementation? Yes. Blocks real ingestion? Yes.** Blocks production? Yes.

### N-03 — There is no consolidated logical data contract to freeze (High)

**Classification:** missing proof / future requirement.
**Files:** `planning-inbox/m10-logical-schema-plan-c2.md` (C2-only, 2026-07-10, pre-dates everything from M13 onward), vs. the concept vocabulary now scattered across `contracts/typed-read-api-mcp-v0-1.md` §5–§9 (request envelope, evidence unit, status lifecycle), `provider-cross-check-proof-v0-1.md` (provider sides, required context tuple, disposition/disagreement vocabularies), `owned-telemetry-overlay-proof-v0-1.md` (evidence windows, alignment output), `searchclarity-proof-workflow-v0-1.md` (report-support request, dispositions, report-safe references), `providers/dataforseo/evidence/` (manifest/inventory/ledger shapes), and five packages of fixture dataclasses.

**What is missing.** The only logical schema plan the repo has ever accepted covers the C2 slice: scope, package, artifact reference, raw manifest, candidate, admitted observation, evidence identity, freshness warning, audit event, rejection reasons. Since then the project minted — in accepted contracts and working code — at least a dozen additional load-bearing concepts (see §10 matrix), each defined in its own document with its own field list, status vocabulary, and identity rules. They are mutually consistent in spirit but have never been reconciled in one place: e.g., the M14 `EvidenceUnit` carries `provider_or_capture_instrument` while the C2 envelope still carries only `capture_method` (the alignment task F-11's reconciliation accepted is still pending); freshness statuses appear as string enums in four packages with no single owner; `scope_class` values differ between fixtures (`market_watch`) and the M10 plan's three-class model. Designing physical schema against thirteen contracts + five fixture files is exactly how a schema goblin is born — each table drawn from whichever document the designer happened to have open.

**Correction.** A dedicated pre-schema milestone (the directive's "physical data-contract freeze," §23 DB-2): one document that enumerates every persistable concept, its identity, its lifecycle states, its relationships, its classification (§10 matrix as the seed), reconciles the known deltas, and is owner-accepted as the *sole* input to physical schema specification. This is a consolidation task, not new design — most of the content exists.
**Gates:** Blocks physical planning? No — this *is* the first physical-planning deliverable. **Blocks physical schema specification? Yes.** Blocks migrations/ingestion/production? Yes (transitively).

### N-04 — The enforcement substrate for spend, duplicates, and authority is still prose + one machine (High)

**Classification:** accepted limitation → pre-ingestion blocker (consolidates the F-01 structural remainder with F-05/F-06/F-07 and the preservation-only ledger).
**Files:** `live_execution.py` (disarmed but still constant-gated; confirmation phrase still a committed string), `campaign.py` (budget math uncalled), committed `attempt-ledger-sanitized.json` (read by no code — verified by grep), gitignored operational registry (machine-local).

**What is wrong.** Everything here is currently *safe* because everything is *off*. But the database phase ends the era in which "off" is the enforcement mechanism: real ingestion means the provider path gets re-armed, and the moment it does, all four deferred defects return live — no clone-stable duplicate substrate, no decision-linked authority record, no cumulative/post-receipt budget enforcement, no attempt lifecycle closure or locking, no preflight in the durable package. The committed sanitized ledger solved evidence preservation (F-02) but nothing consults it, so a fresh clone still has zero spend memory the code can see.

**Correction (design now, build at the ingestion gate).** A committed `provider-authority` record (decision path + recipe + remaining-authorized-count, normally 0) read by preflight; the committed ledger as the duplicate substrate, updated atomically with terminal statuses; cumulative stage/campaign budget checks wired pre-send; post-receipt cost stop; preflight persisted as package artifact `01-*`; non-committed confirmation values. The database phase adds one more requirement: idempotent ingestion keyed on the duplicate-prevention key, so a re-run cannot double-admit (see §11 concurrency hammers).
**Gates:** Blocks physical planning? No. Blocks migration implementation? No. **Blocks real ingestion? Yes — hard.** Blocks production? Yes.

---

## 8. Medium and Low Findings

**N-05 (Medium, proven, F-04 regression).** `README.md`: "As of 2026-07-12, M13 is closed and M14 typed read API / MCP contract planning is active." `LLM_START_HERE.md:113`: "For the active M14 planning boundary, do not start:" — two lines after line 111's rule "Do not hard-code a milestone from this file." Both statements survived six closure decisions because the Batch A fix updated the *values* instead of removing the *restatements*. A rule-following fresh session hits line 125's drift-stop rule ("If another root file disagrees with ACTIVE_CONTEXT.md, stop") and correctly halts — so the failure mode is wasted sessions, not unsafe action, but it is the third occurrence of this class. Correction: delete the phase restatements entirely; README says "phase authority lives in ACTIVE_CONTEXT.md," full stop; LLM_START_HERE's non-implementation section points at ACTIVE_CONTEXT's non-goals. Blocks nothing; fix before the database roadmap adds twelve more closures to go stale against.

**N-06 (Medium, open owner rulings).** OR-C2 (durable vs manifest-only vs capture-and-purge vs no-storage, per source family) and OR-C4 (raw archive layout: filesystem/object-store/hybrid) remain open. Raw-support persistence cannot be physically designed without them: the retention posture determines whether raw tables/buckets exist at all per family, and the layout ruling determines whether the database stores payloads or pointers+hashes (V12 says pointers; the layout of what they point *at* is unruled). Blocks physical schema specification for raw support; does not block the rest of the freeze.

**N-07 (Medium, accepted limitation → blocker).** Encryption/off-machine backup remains `blocked_pending_owner_tool_and_key_path`. Correct for v1. Before one real observation is durably persisted, the recovery posture must include: encrypted backup with owner-held keys, at least one verified off-machine generation, and a database-level backup/restore proof (see §19). A repository bundle does not back up a database.

**N-08 (Medium, contract/prototype delta).** Contract §15 requires "cursor expiration"; prototype cursors (HMAC payload: caller/scope/type/intent/offset/contract) carry no expiry and none is enforced. The register's limitations list does not disclose the delta. Harmless at fixture scale; at DB scale an eternal cursor is a replayable bookmark across evidence-status changes (a stale-read vector interacting with N-01). Fix with §15 corrections.

**N-09 (Low).** Accepted `typed-read-api-mcp-v0-1.md` §24 asserts the Hermes lineage is "not yet consumed" — falsified the same day by the lineage review. An accepted contract asserting a resolved gap is a small internal contradiction; amend §24 (with a change-log entry) at the next contract touch.

**N-10 (Low, pattern).** `fixtures.EVIDENCE`/`GRANTS` are mutable module-level dicts; I mutated them at runtime in one line. Acceptable in a read-only prototype; the DB phase must replace direct fixture access with repository interfaces so storage immutability is a property of the substrate, not of nobody-calling-`dict.__setitem__`.

**N-11 (Low, latent authz).** `freshness_check` authorizes its own type, then calls `evidence_lookup`, which authorizes *its* type — so `freshness_check` implicitly requires the `evidence_lookup` grant. No fixture caller has the failing combination, so no test can see it. Define capability implication explicitly in the authorization model (either grants are closed under composition, or nested calls run under the outer authorization context).

**N-12 (Low).** `_CURSOR_KEY` is a committed constant. Fine for fixtures; the DB/network phase needs a managed-secret + rotation posture, which belongs in the same secret-posture ruling M19 already opened.

**N-13 (Low, unproven contract behavior).** `consumer_promotion_required` is hard-coded `False`; no fixture ever approaches promotion, so contract R11-equivalent behavior (skeleton R11; typed-read contract's promotion boundary) has zero executed proof. Add a fixture whose claim intent forces the flag.

**N-14 (Low, pattern).** M15 silently remaps its claim intents (`provider_metric_statement` → `historical_observation`) before calling M14. The mapping is conservative and correct, but undocumented intent translation between contract layers is a semantic-drift channel; record layer mappings in the consumer contract explicitly.

---

## 9. Doctrine and Physical-Enforcement Audit

The doctrine survives on paper and in fixture code. The question the directive asks is which rules have a credible *physical* enforcement path. Verdict: **every doctrine rule has a credible path; none currently has physical enforcement; four rules are at elevated risk of being "enforced" only by application code unless the schema spec is explicit.**

### Contract rule → proof level → future database enforcement → required hammer → blocking gate

| Contract rule (source) | Current proof level | Future database enforcement | Required hammer (§11) | Blocking gate |
|---|---|---|---|---|
| Scope on every record; no cross-scope reads (scope-rights-retention; H1) | fixture/in-memory (grants dict; scope checks in five packages) | NOT NULL scope FK on every evidence table + scope-aware repository layer + (optionally) DB row-level security for defense-in-depth; cross-scope joins absent from read queries by construction | wrong-scope write/read; cross-scope aggregation | migration acceptance |
| Rights fail-closed (H2) | fixture validation (enum allow-lists) | rights_class as governed vocabulary table + NOT NULL FK + CHECK against blocked classes on insert path; admission-time application enforcement primary | unknown-rights insertion; rights downgrade propagation | migration + ingestion |
| Retention fail-closed; purge real (H3) | fixture validation + one real purge (C00, hash-proofed) | retention_class NOT NULL; retention state machine as data (not prose); purge = state transition + physical deletion job + audit event in one transaction; partial index on purge-due | retention downgrade; purged-represented-as-retained; purge racing read | ingestion + operations |
| Append-only observations; supersession not overwrite (H19; V9) | frozen dataclasses only — **no substrate proof** | no UPDATE/DELETE grants on observation tables for the app role; correction = new row + status transition; DB triggers or revoked privileges, not convention | silent historical overwrite; two writers updating "immutable" evidence | migration acceptance (this is *the* schema-shape decision) |
| Audit-first, same-transaction (H21; V9/N4) | returned tuples only — **no substrate proof** | audit event insert in the same transaction as every consequential transition; injected audit-failure rollback test | admission-without-audit; audit-write failure rollback | migration acceptance |
| Evidence ID ≠ row ID ≠ provider ID ≠ raw ID (evidence-id-citation; H15) | fixture (distinct random IDs) | evidence_id as its own unique, non-sequential, application-minted key; **never** the serial PK; provider job IDs in attribution columns only; raw pointers internal-only (OR-D2 ruled) | row-ID/evidence-ID coupling; raw-ID-as-citation; duplicate evidence identity | schema spec |
| No strategy/recommendation/conclusion persistence (H5; boundaries) | structural allow-lists + marker tests | **no schema for it** — the strongest enforcement is absence: no notes/metadata free-text columns on evidence tables without a governed vocabulary; closed envelopes at write path; periodic contamination hammer over any JSON columns | strategy-as-metadata; recommendation-as-notes; derived-conclusion-as-observation | schema spec + every migration |
| No customer records / first-party storage (H4; S4/K1) | structural field rejection (M15/M17) | no customer tables, no customer_id columns anywhere in Observatory schema; overlay path has no INSERT privilege on evidence tables at the DB-role level | customer-identity leakage; overlay-persistence attempt at the role level | schema spec |
| Provider testimony, attribution mandatory, disagreement preserved (provider-testimony/cross-check; H8; OR-A1 ruled) | fixture comparator; compute-on-read ruled | provider attribution NOT NULL on provider-derived metrics; no winner/composite/average columns; **no disagreement tables** (OR-A1) — read model only | provider score without attribution; disagreement collapsed into winner (schema-level: attempted table) | schema spec |
| Freshness/claim caveats travel with evidence (H9/H10) | fixture guard + warning strings | captured_at NOT NULL, timezone-enforced (CHECK); freshness computed on read (not stored as truth); caveat fields non-detachable at the read layer (application) | stale-without-warning; caveat-stripped projection | read-slice acceptance |
| Panel version immutability (query-panel; H14) | not exercised (panels deferred since M10) | versioned definition tables: new version = new row; used versions have no UPDATE path | panel-version mutation; ambiguous panel version | deferred until panels are activated |
| Raw manifest hash/pointer integrity (raw-archive; H12) | one real cycle (C00) + fixture manifest checks | manifest table with NOT NULL sha256/bytes/media-type; pointer validity job; hash re-verify on read of raw-supported evidence | hash mismatch; pointer/hash mismatch; manifest survival when forbidden | ingestion (needs OR-C2/C4 first) |
| Typed reads only; no SQL/credentials to LLMs (H17; K9) | fixture authz | DB credentials held by the API layer only; a **read-only database role** for the read path distinct from the ingestion role; no credential material in any response (proven pattern exists) | direct-SQL attempt; credential exposure; role-privilege probe | read-slice acceptance |
| Overlay no-storage (overlay; H16; OR-F1/F2) | code-path discard (honestly bounded) | overlay path runs under a DB role with zero INSERT/UPDATE on evidence tables; overlay values excluded from logs by structured-logging policy; infrastructure-level guarantees deferred (M17's own limit) | overlay-persistence via role; overlay value in log capture | real-overlay gate (post-DB) |

**Elevated-risk rules** (application-only enforcement unless the spec is explicit): append-only (developers reach for UPDATE), audit-first (developers reach for two transactions), evidence-ID independence (ORMs reach for the PK), and no-strategy-persistence (free-text columns accrete). All four must be named schema-spec requirements with role/constraint/trigger decisions, not left to the write path's good manners.

**Schema-goblin watchlist** (directive §9), checked against current planning: one-giant-observations-table — the M10 plan already resists it (distinct responsibilities), but the freeze must decide per-family observation tables vs. a typed core + family extensions *explicitly*; JSON dumping ground — V5/V12 three-layer rule holds on paper; the freeze must cap JSON columns to raw-support manifests and bounded metadata with governed keys; customer_id leakage — no current concept carries it; keep it that way by scope-translation at consumers (V15); mutable history — see append-only above; purged-as-available — retention state machine must be data (the C00 ledger's `raw_state: purged_with_proof` is the right seed vocabulary).

---

## 10. Logical Schema Readiness Audit

Readiness assessment per concept, with the classification matrix the directive requires. Maturity legend: **ready** (identity, lifecycle, and fields stable across contracts and code), **near** (stable concept, known deltas to reconcile), **under-specified** (real gaps), **unresolved** (open ruling blocks it).

| Concept | Classification | Maturity | Notes / gaps |
|---|---|---|---|
| scope | durable entity | ready | Flat scope + scope-class (Q1 ruling). Delta: fixture `scope_class="market_watch"` strings vs. governed vocabulary — freeze must bind the enum |
| scope class | versioned definition (vocabulary) | ready | Three classes ruled; OR-G3 (new classes) properly open |
| query panel / panel version / panel item | versioned definition | **under-specified** | Contract exists (accepted) but deferred since M10; never exercised in any fixture; no code touches it. Do not build tables in the first slice; freeze records it as owned-but-deferred (V10 discipline) |
| capture package / capture attempt | durable entity + append-only event | near | C2 envelope + M13 manifest are two shapes of one concept; align fields (incl. `provider_or_capture_instrument` vs `capture_method` — the accepted F-11 reconciliation task, still pending) |
| provider / capture instrument | versioned definition (registry) | near | V7 registry pattern + providers/ folder exist; needs a first-class instrument identity the capture package references |
| observation (candidate / admitted) | durable entity, append-only | ready | C2 proves the candidate/admitted split; per-family typing decision belongs to the freeze |
| evidence ID | durable identity | ready | Non-enumerable, status-aware, internal-only — all ruled (OR-A4/OR-D2/OR-D3). Minting/collision-domain spec is the freeze's job (bare uuid4 is provisional per reconciliation) |
| citation handle (internal) | derived (from evidence ID) | near | `cite:<id>` provisional; fine to derive, never store separately |
| report-safe reference | external consumer concern | ready as boundary | M15 ruled synthetic/artifact-local; **forbidden as Observatory persistence** — mapping lives with the consumer artifact |
| raw payload manifest / raw support status | manifest only / durable state | **unresolved** | Blocked by OR-C2 (posture per family) and OR-C4 (layout). Status vocabulary (`purged_with_proof`, `not_captured`, `blocked_by_rights`, `unknown`) is already good |
| shape fingerprint | append-only event (per capture) | near | One canonical versioned algorithm still required (F-12 gate) before any second payload |
| parser version / provider drift event | versioned definition + append-only event | **under-specified** | Named in contracts (H13) but no code, no vocabulary, one payload. Design the event shape at the freeze; populate only when a second sample is authorized |
| rights classification / retention classification | versioned vocabularies + per-record state | ready / **unresolved** | Rights vocabulary ruled (K3 six-way). Retention *vocabulary* exists; retention *posture per family* is OR-C2 |
| freshness state | derived read model | ready as computed | Statuses consistent across four packages but unowned — freeze binds one vocabulary; never stored as truth (compute from captured_at + volatility class) |
| volatility class | versioned vocabulary | **under-specified** | Only `moderate`/`unknown` exist in fixtures; honest vocabulary requires repeated real samples (prior audit's trust item 5) — persist the *label*, defer the science |
| claim-safety state | derived read model | ready | M15 disposition/blocker vocabulary is the seed; computed, never stored |
| audit event | append-only event | ready | M10's six-event minimum + M14's security-log separation (OR-D5) — two distinct stores, evidence-audit inside the DB, access logs outside |
| provider disagreement read model | derived read model | ready | **OR-A1 ruled: forbidden persistence.** M16 comparator vocabulary is the read-model spec |
| consumer promotion reference | external consumer concern | near | Promotion is a contract, not storage; the only Observatory-side datum is possibly a promotion-required flag on read output (computed — see N-13) |
| caller grant (authz) | versioned definition | near | OR-D1 ruled the model; grant storage/administration is API-layer, arguably outside the evidence DB entirely — freeze must place it explicitly |
| overlay values / overlay windows | ephemeral input / derived read model | ready as boundary | **Forbidden persistence** (ruled); evidence windows are computed from observations at read time |
| cross-scope aggregates | forbidden persistence | ready as boundary | OR-G1 open, forbidden by default |
| strategy / recommendation / conclusion / report prose / customer record | forbidden persistence | ready as boundary | The freeze should carry the forbidden list forward verbatim so schema review can diff against it |

**Overloaded-entity risk:** the observation concept is the one candidate for overloading — SERP items, keyword metrics, AI citations, page snapshots, and manual observations have very different bodies. The freeze must make the typed-core-plus-family decision consciously (V18/K6: distinct families, never collapsed) rather than letting the first migration decide by default.

---

## 11. Database Hammer-Readiness Audit

Current hammer state, honestly classified: H1–H22 are **defined** (draft matrix); a large subset is **covered by fixture/unit tests at contract level** (scope, rights, retention, envelope, strategy/customer rejection, ID confusion, freshness, hostile input, attribution, overlay no-storage, read authorization); H7/H12 partially have **one owner-local real execution** behind them (C00); H14 (panels), H22 (migrations), H20-as-real-concurrency, H21-as-real-transactions, H19-as-real-immutability are **not yet executable** — no surface exists; H2/H3/H13 have **shape but not substrate** proof. Nothing is at `real_surface_executable`-passed for persistence semantics, which is exactly what the acceptance-gate policy's own vocabulary predicts.

## Database Hammers That Must Fail Before We Trust The Database

The recommended database hammer program. Every hammer below is written to *fail* against a naive implementation — if it cannot fail, it proves nothing. Columns: risk / layer / setup / expected result / CI / real Postgres / blocks.

### A. Scope and contamination

| Hammer | Risk protected | Layer | Setup | Expected | CI | Real PG | Blocks |
|---|---|---|---|---|---|---|---|
| DB-A1 wrong-scope write | scope contamination | repository + constraint | two scopes, writer bound to scope A inserts scope-B row | rejected (app) AND constraint-visible | yes | yes | migration acceptance |
| DB-A2 wrong-scope read | leakage | read slice | caller granted A queries B via every request type + cursor replay | uniform not-found/blocked_scope; no count/existence leak | yes | yes | read slice |
| DB-A3 cross-scope aggregation | OR-G1 breach | read slice + query review | request crafted to join scopes (incl. via cursor tamper) | rejected | yes | yes | read slice |
| DB-A4 customer-identity insertion | H4 | write path + schema review | rows carrying customer_id/email in every writable column incl. JSON metadata | rejected; schema has no home for it | yes | yes | migration acceptance |
| DB-A5 overlay-persistence via role | H16 | DB roles | overlay-path role attempts INSERT/UPDATE on evidence tables | privilege denied at DB level, not just app | yes | yes | real-overlay gate |
| DB-A6 strategy-as-metadata | H5 | write path + periodic scan | recommendation text in every free-text/JSON field, paraphrased (no markers) | closed envelopes reject unknown fields; governed-key JSON rejects free text | yes | yes | migration acceptance |

### B. Rights and retention

| Hammer | Risk | Layer | Setup | Expected | CI | PG | Blocks |
|---|---|---|---|---|---|---|---|
| DB-B1 unknown-rights insert | H2 | constraint + app | rights_class NULL / not-in-vocabulary / blocked class | insert fails (CHECK/FK) | yes | yes | migration acceptance |
| DB-B2 rights downgrade propagation | post-admission rights change | state machine + read | flip a row to blocked_by_rights; read immediately | evidence returns blocked status, never active; dependent reads honor it | yes | yes | read slice |
| DB-B3 purged-represented-as-retained | H3/H12 | retention job + read | purge raw support; read raw_support_status; attempt raw resolution | `purged_with_proof`; resolution refuses | yes | yes | ingestion |
| DB-B4 retention race with active read | H3×H20 | transaction/isolation | purge transaction concurrent with evidence read | reader sees pre- or post-purge state coherently; never a pointer to deleted bytes with `retained` status | yes | yes | operations acceptance |
| DB-B5 manifest survival when forbidden | H3 | retention job | family posture = no manifest; purge runs | no residual manifest row | yes | yes | ingestion (needs OR-C2) |

### C. Identity and integrity

| Hammer | Risk | Layer | Setup | Expected | CI | PG | Blocks |
|---|---|---|---|---|---|---|---|
| DB-C1 duplicate evidence identity | H15 | unique index | insert same evidence_id twice, concurrently | second fails; unique index proof | yes | yes | migration acceptance |
| DB-C2 row-ID/evidence-ID coupling | H15 | schema review + test | dump a read response; assert no serial PK appears; renumber rows in a restore and re-resolve handles | handles resolve identically after PK renumbering | yes | yes | migration acceptance |
| DB-C3 raw-ID/provider-ID as citation | H15 | read slice | request citation for raw/provider IDs | not_found/blocked; only evidence handles resolve | yes | yes | read slice |
| DB-C4 hash / pointer mismatch | H12 | ingestion + read | corrupt stored payload or pointer; re-verify | admission blocked / read flags integrity failure | yes | yes | ingestion |
| DB-C5 observation without capture context | H6 | NOT NULL constraints | insert observation missing package/provenance FK | constraint failure | yes | yes | migration acceptance |
| DB-C6 silent historical overwrite | H19 | privileges/triggers | UPDATE an admitted observation's provenance as the app role; as a superuser-shaped role | app role: denied at DB; audit records any privileged path | yes | yes | migration acceptance |
| DB-C7 silent partial view (from N-01) | coverage honesty | read slice | scope with rows ≫ every ceiling; walk all pages | final page discloses omission; counts accurate | yes | yes | read slice |

### D. Concurrency and idempotency

| Hammer | Risk | Layer | Setup | Expected | CI | PG | Blocks |
|---|---|---|---|---|---|---|---|
| DB-D1 duplicate provider-result ingestion | double-admit | idempotency key + unique index | ingest identical capture twice, concurrently (two processes) | one admission; second returns first's identity | yes | yes | ingestion |
| DB-D2 concurrent capture admission race | H20 | transactions | two writers admit same CapturePackage simultaneously | exactly one wins; loser gets deterministic duplicate error | yes | yes | ingestion |
| DB-D3 same idempotency key, changed shape | spoofed replay | ingestion | reuse duplicate key with altered payload | rejected (shape-hash bound) | yes | yes | ingestion |
| DB-D4 two writers on immutable evidence | H19×H20 | privileges + isolation | concurrent supersession of one observation | two superseding rows or one winner — never lost/merged history | yes | yes | ingestion |
| DB-D5 purge racing admission | H3×H20 | transactions | retention purge concurrent with admission referencing same raw support | consistent terminal state; audit shows ordering | yes | yes | operations |
| DB-D6 drift racing parser admission | H13×H20 | ingestion | shape-fingerprint mismatch arriving mid-admission | quarantined; no partial observation | yes | yes | provider re-entry |

### E. Migration

| Hammer | Risk | Layer | Setup | Expected | CI | PG | Blocks |
|---|---|---|---|---|---|---|---|
| DB-E1 forward + rollback pair | H22 | migration harness | every migration | rollback tested, restores prior schema + data | yes | yes | **every migration** |
| DB-E2 failed-migration recovery | partial state | harness | inject failure mid-migration | recoverable; documented procedure executes | yes | yes | migration acceptance |
| DB-E3 constraint vs dirty data | silent constraint skip | harness | add constraint against seeded violating rows | migration fails loudly; remediation path documented | yes | yes | every migration |
| DB-E4 vocabulary evolution | enum drift | harness | add/retire rights/retention/status values | old rows readable; retired values write-blocked | yes | yes | migration acceptance |
| DB-E5 old reader / new schema, new reader / old schema | version skew | read slice + harness | run N−1 read code against N schema and vice versa | deterministic failure or compatibility, per declared policy | yes | yes | operations |
| DB-E6 backup-before / restore-after migration | H22×M19 | ops | full DB backup, migrate, restore, verify evidence-ID resolution + hashes | resolution and hashes identical | partially (nightly) | yes | **first real observation** |

### F. Typed-read and authorization (database-backed)

| Hammer | Risk | Layer | Setup | Expected | CI | PG | Blocks |
|---|---|---|---|---|---|---|---|
| DB-F1 direct SQL attempt | H17 | API surface | every injection-shaped input in every filter field | closed vocabulary rejects; parameterized queries only (code review + test) | yes | yes | read slice |
| DB-F2 credential exposure | H17 | response scan | scan every response/error/log for credential material | none, ever | yes | yes | read slice |
| DB-F3 read-role privilege probe | least privilege | DB roles | read-path role attempts INSERT/UPDATE/DDL | denied at DB | yes | yes | read slice |
| DB-F4 handle enumeration | existence oracle | read slice | sequential/guessed handles across scopes at volume | uniform not-found; rate ceiling trips; access log records | yes | yes | read slice |
| DB-F5 pagination abuse / exhaustive extraction | scrape shape | read slice | walk entire scope; widened-filter cursor replay; expired cursor | ceilings + disclosure (DB-C7); cursor rebinding rejected; expiry enforced (N-08) | yes | yes | read slice |
| DB-F6 stale-without-warning | H9 | read slice | current-use claim over stale rows seeded in DB | blocked or degraded-with-warning | yes | yes | read slice |
| DB-F7 attribution stripped / winner collapse | H8 | read slice | field-projection and comparison requests attempting to drop attribution or request winners | non-detachable attribution; winner request rejected (OR-A1) | yes | yes | read slice |
| DB-F8 raw-pointer leakage | OR-D2 | response scan | every response/error path scanned for paths/pointers | status only, never pointers | yes | yes | read slice |

All CI-marked hammers should run against real Postgres (containerized) — not SQLite stand-ins — because half of them test Postgres-specific behavior (privileges, isolation, constraints). That is the single infrastructure requirement this audit endorses; nothing heavier is needed.

---

## 12. Code and Test Audit

**Package boundaries match contracts** cleanly: five packages map one-to-one onto the C2, probe, typed-read, SearchClarity, cross-check, and overlay contracts, and dependency direction is correct (M15 → M14; nothing imports upward). No accidental production-shaped code hides behind "prototype": no network listener, no DB driver, no scheduler, no dashboard — verified by inspection and by the absence of any such import.

**Tests are substantially genuine.** The 29-suite corpus asserts behavior (error codes, response fields, rejection paths), not just happy output; hostile-path suites exist per milestone; determinism suites exist; no-side-effect suites check module state before/after; the M17 false-positive fix commit shows the team distrusts its own green. Forbidden-path tests are real in the sense that the code paths exist and reject.

**Where the ceiling sits — the honest proof-limit inventory:**

- **Assertions that inspect flags:** the overlay "discard" proof asserts `build_discard_status()` returns `"discarded_after_response_build"` — a string, not an erasure. M17's register says so; preserve that humility.
- **Tests that would pass if a real database violated the law:** all of H19/H21/H22-adjacent tests. `frozen=True` proves Python raises on attribute assignment; it proves nothing about UPDATE.
- **Tests relying on fixture immutability rather than storage immutability:** all of them, structurally (N-10 — I mutated `EVIDENCE` in one line).
- **Fixture values creating false confidence:** N-01 is the proven instance — every fixture scope holds ≤ 4 visible units against a ceiling of 4, so the silent-drop branch is dead code to the suite. The generalization: fixture populations must exceed every ceiling, boundary, and page size by construction in the DB harness.
- **No atomicity, rollback, or audit-transaction verification exists** — correctly impossible today; §11 E-series owns it.
- **Determinism is genuinely deterministic** within the fixture world (sorted keys, canonical JSON, static IDs) — but `request_id: "req_fixture_static"` means response-identity design (unique, non-replayable response IDs) is still open for the DB slice; M15's hash-derived `scr_*` response IDs are the better pattern to generalize.
- **Error taxonomy is coherent** and uniform (`blocked_*` house style; uniform `not_found`), with one latent coupling defect (N-11).

**Tests needing replacement or supplementation at persistence:** every scope/rights/retention/append-only/audit test re-derived against the substrate (the project's own reconciliation already commits to this); every ceiling test re-seeded with over-ceiling populations; authorization tests re-run against DB roles, not dicts; plus the entire §11 program. Tests that carry forward unchanged: contract-shape suites, error-taxonomy suites, claim-intent/caveat suites, comparability classification, overlay request validation.

---

## 13. M13 Provider / Raw-Evidence Reassessment

Reassessed for the database phase specifically:

**What future persistence must preserve from provider captures** — the C00 package is the template and it is nearly complete: request manifest (recipe, endpoint, request hash, duplicate key, ceilings, rights/retention/claim labels), response summary (statuses, costs), field inventory (versioned, parameter-declared), item-type summary, cost reconciliation (multi-witness, conservative), incident records with terminal statuses, purge proof (hash, bytes, containment, absence). The two known gaps carry forward as future-package requirements: the authorizing preflight (F-07) and a closed attempt lifecycle (F-06). The committed sanitized ledger's status vocabulary (`provider_authentication_error`, `reviewed_complete_raw_purged`) is the seed for the capture-attempt entity's lifecycle states.

**Is the retained evidence enough to design the provider/capture manifest structures?** For *structure*, yes — manifests, request/response identity, cost evidence, incident evidence, raw-support state, and purge state can all be modeled from what is committed. For *content typing* (which item-family fields get promoted columns), emphatically no.

**What must not be inferred from C00 — the explicit warning the directive asks for:** one payload, one keyword, one locale, one device, one depth, one endpoint, one day. Do not design item-family tables, field promotions, volatility classes, drift baselines, or "stable field" lists from it. The post-pull review's own sentence — "This complexity is evidence against designing a physical schema from one payload" — should be quoted inside the data-contract freeze. The correct database posture for provider evidence at first ingestion is: typed provenance core + raw-support-first bodies, with field promotion earned per family by multiple authorized samples under the canonical fingerprint (F-12 gate). Designing the database around the DataForSEO C00 shape would be building the telescope around one photograph of one star.

---

## 14. M14 Typed-Read Database-Transition Review

**Stable semantics (survive persistence unchanged):** the four request types; closed claim-intent vocabulary; per-caller scope/request grants (OR-D1); uniform not-found; status-aware lifecycle (OR-D3); non-detachable caveats; untrusted-content envelope; no-side-effect law; error taxonomy; security-log separation (OR-D5).

**Fixture-dependent (must be redesigned, not ported):** the `EVIDENCE` dict → repository interface over indexed queries; static request/response IDs → unique per-response identity; grants-in-code → grant administration outside the evidence DB (freeze decision, §10); cursor offsets → keyset pagination (offset cursors over mutable-status data misbehave; keyset on `(captured_at, evidence_id)` is the deterministic-ordering answer the contract already implies); the hard-coded HMAC key → managed secret (N-12); freshness computed from string statuses → computed from `captured_at` + volatility class at read time.

**Filters requiring indexes:** scope_id (every query), (scope_id, evidence_status), (scope_id, source_family), (scope_id, captured_at) for keyset ordering and freshness, evidence_id unique. Nothing exotic; the closed filter vocabulary was designed well enough that the index set is small and knowable.

**Which warnings computed vs stored:** stored — captured_at, statuses, rights/retention classes, volatility label, static caveat text tied to source family; computed — freshness_status, claim fitness, coverage/blind spots, disagreement output, `consumer_promotion_required` (N-13), truncation disclosure (N-01).

**Recommended minimum database-backed read slice** (eventual DB-6 in §23): `evidence_lookup` + `observation_package_read` only, over the persisted synthetic C2-family slice, under two caller classes (internal_llm, operator), with DB-F1–F8 and DB-C7 hammers, keyset cursors with expiry, and the read-only DB role. `freshness_check` and `coverage_blind_spot_read` follow once freshness computation and coverage derivation are DB-backed. No MCP registration, no network listener, no production auth — those remain deferred exactly as the contract's §23 says.

---

## 15. M15 SearchClarity Consumer-Boundary Review

The proof demonstrates the right thing: SearchClarity receives **evidence support** — disposition-classified, caveat-carrying, reference-mapped packs — and never report prose, recommendations, or customer context. The structural allow-list on request fields plus the forbidden-field rejection (customer/overlay/report/recommendation keys) is the correct primary mechanism; the disposition classifier correctly blocks on rights/retention/attribution/absence/freshness grounds and downgrades superseded/stale evidence to `historical_support_only`.

**What remains synthetic and must stay visible:** report-safe references are artifact-local synthetic mappings (OR-E1's exact ruling); no real customer, engagement, or report has touched anything; final report *language* validation (DR9) is untested and deferred; overlay behavior in M15 is blocked-path proof only (OR-F1 M15-scope).

**Does database design need any fields solely for SearchClarity? No — and it must not get any.** The reference mapping is derivable (scope + evidence-ID list → deterministic synthetic refs) and belongs in the consumer artifact layer; persisting it Observatory-side would create the first consumer-specific table and the first customer-adjacent join point. The only Observatory-side accommodations SearchClarity legitimately needs are already consumer-neutral: durable evidence-handle resolution, status-aware reads, and (eventually, O-8) as-of reads. Claim-safety context already travels with evidence by construction. What must survive persistence for M15's sake: evidence handles must resolve identically forever (DB-C2), and the disposition classifier's inputs (statuses, attribution, caveats, freshness) must be non-detachable read fields.

One pattern to govern: the silent claim-intent remapping (N-14) — record layer translations in the consumer contract.

---

## 16. M16 Provider-Disagreement Persistence Review

OR-A1 is ruled and the ruling is correct: **compute-on-read only; no persisted disagreement ledger, cache, or table without a later V6 materialization proof and a new owner ruling.** This audit endorses keeping that as the database-phase default and adds the schema-level consequence: the physical schema must contain *no* disagreement entity, and the DB-F7 hammer should include an attempted-materialization probe (a migration adding a disagreement table must fail schema review by construction — put it on the forbidden-persistence list in the freeze).

**What disagreement *does* need from the database:** everything it consumes must be durable and honest per-side — provider attribution NOT NULL, metric name/unit/definition/posture fields, capture context (the M16 required-context tuple: subject, surface, locale, language, device, location), captured_at and provider_reported_time for distance computation, and evidence status. Non-synchronous observation is handled correctly today (capture-distance seconds surfaced, freshness misalignment downgrades comparability) — persistence just needs to not lose the timestamps. Provider personality/profile metadata (systematic biases) is a legitimate *future* observation family about instruments, not a truth adjustment — park it; do not fold it into v1 schema.

**Missing values and proprietary scores:** the `unresolved_incomparability` posture must survive as computed output; the temptation at DB scale will be to "fill in" missing definitions with assumed comparability. The hammer: two sides, one proprietary undefined metric → any disposition other than unresolved is a failure.

---

## 17. M17 Overlay No-Storage Persistence Review

The fixture proof is honest about its ceiling and the ceiling is real: code-path discard proves the *application* doesn't persist; it cannot prove memory, swap, tracing, or log pipelines don't. For the database phase, the no-storage law gains its first *physical* enforcement opportunity, and it should take it:

- **DB roles:** the overlay/alignment path runs under a role with SELECT-only on evidence tables and zero privileges elsewhere (DB-A5). This converts "the code doesn't write" into "the code *cannot* write."
- **Identity firewall:** overlay inputs already reject evidence/observation/capture IDs in values (`_FORBIDDEN_KEYS`) — keep that, and add the inverse at persistence: no Observatory table may reference an overlay by any identity, because overlays have none.
- **Logging policy:** structured logging with an explicit field allow-list on the overlay path; overlay `values` never enter log records; the access log (OR-D5) records that an alignment ran, never what was aligned.
- **Error handling:** exception paths must not serialize request bodies (the current `deepcopy` + validation-first pattern is right; keep validation before any operation that could log).

**Before any *real* private telemetry overlay is allowed** (the directive's explicit question): the role-level write prohibition proven (DB-A5), the logging allow-list proven by log-capture test, tracing/APM either absent or field-scrubbed by proof, a memory posture statement (accepting that Python cannot guarantee erasure — say so, as M17 already does), request isolation (no shared caches across requests — extend the M17 cache-safety test to the real serving layer), and an explicit owner ruling re-opening OR-F2 for real data. None of this blocks the database phase; all of it blocks real overlays.

---

## 18. M18 Recurring-Watch Policy Review

The rejection-plus-policy is sound as a future foundation, and better than sound: cadence classes capped at weekly-candidate; per-run *and* rolling-30-day ceilings; no automatic retries, increases, fallbacks, or shape changes; duplicate keys binding scope + immutable panel version + recipe + provider + window + shape-hash; mandatory human review at first execution, first success, every failure, and every parameter change; explicit stop conditions including owner-disable. This is the M13 spend discipline generalized correctly.

**Is recurrence a prerequisite for the database phase? No** — confirmed. Nothing in DB-1..DB-9 (§23) needs a scheduler, and building one now would violate the policy's own review-gate design (nothing exists to review).

**Database structures that should remain deferred until recurrence is authorized:** scheduler/job/queue tables, panel-run-schedule tables, cadence state, failure-budget counters, and any panel tables at all (§10 — panels are owned-but-deferred; V10 forbids ad-hoc tables for deferred domains). The only recurrence-relevant thing the first schema should do is *not preclude* it: the duplicate-prevention key design (DB-D1/D3) should accept the M18 key components (window, panel version) as future fields without redesign.

---

## 19. M19 Recovery and Operations Review

**What the proof genuinely proves:** the Git repository — full history — can be bundled, hash-verified, restored to an exact HEAD, fsck-validated, and re-tested to 184/184, with prohibited ignored roots absent from the restore. That is a complete and competent *repository* recovery proof, and it was sufficient for the bounded v1 acceptance because v1's only durable asset *is* the repository (plus preserved local artifacts, which the cleanup posture protects).

**What it does not prove** (M19's own classification, confirmed): encrypted backup (blocked on owner tool/key path — N-07), off-machine storage, multiple generations, cloud/workstation/production recovery, and — decisive for this audit — **anything about database recovery**, because no database exists.

**Database backup/restore requirements to add before persistence** (feeding DB-7 in §23): (1) `pg_dump`/physical-backup posture chosen and ruled (logical dumps suffice at first-slice scale; point-in-time recovery is a later operational maturity item, not a first-slice requirement — don't gold-plate); (2) backup-before-migration as a hard harness step (DB-E6); (3) restore proof that verifies not just row counts but *evidence semantics*: evidence-ID resolution, raw-manifest hashes, audit-event continuity, and scope isolation post-restore; (4) at least one encrypted, off-machine generation before the first *real* (non-synthetic) observation persists — this is where N-07 stops being acceptable; (5) secret posture extended to database credentials and the cursor/signing keys (N-12) under the M19 secret rulings' framework; (6) the preserved-artifact protection extended to database backup artifacts.

---

## 20. M20 Acceptance Correctness Review

Answering the directive's questions directly:

- **Was accepting v1 at the bounded ceiling justified?** Yes. The proof corpus (184 verified tests, five result registers, one real governed provider cycle, restore proof) matches the acceptance language.
- **Did the acceptance language accurately describe the proof?** Yes — unusually so. Every claim in the acceptance decision's proven-list is traceable to an artifact this audit inspected, and each carries its bounding adjective ("bounded local prototype," "synthetic," "code-path," "repository archive").
- **Were known limits omitted?** No material omission found. Two additions this audit would have made: the extraction-ceiling disclosure gap (N-01 — unknown at acceptance time; found only by adversarial probing) and the still-draft hammer authority (N-02 — knowable at acceptance; the register mentions proof classes but not that OR-B1/B2 remain unruled).
- **Was any unproven behavior represented too strongly?** One phrase deserves tightening: ACTIVE_CONTEXT's "Hammer tests are a hard gate for implementation" — true as intent, but the gate's definition is an unruled draft (N-02). The acceptance decision itself avoids the word "hammer" in its proven-list, which is to its credit.
- **Did closure create stale or conflicting authority?** Yes — README and LLM_START_HERE (N-05), the recurrence of the previously-fixed class.
- **Does the repo clearly show no active milestone?** Yes (ACTIVE_CONTEXT, handoff, roadmap all agree) — except the two stale files.
- **Can a future model mistakenly infer production permission?** From the decisions, no — the non-authorization lists are exhaustive and repeated. From README/LLM_START_HERE, a model could mistakenly infer *M14 planning* permission, which is milder but real.
- **Are post-v1 gates sufficiently explicit?** Yes: "Any further work requires a new explicit owner-approved roadmap or bounded decision."

**M20 verdict: PASS WITH REQUIRED CORRECTIONS** — the corrections being N-05 (stale authority created/left by closure) and a one-line acceptance-adjacent clarification that the hammer *gate policy* remains draft pending OR-B1/B2 (so the "hard gate" phrase cannot be read as an accepted definition). Neither correction disturbs the acceptance itself.

---

## 21. Open Owner Rulings That Block Physical Design

From the verified tracker, exactly these gate the database phase (everything else open is correctly parked):

| Ruling | Blocks | When needed |
|---|---|---|
| **OR-B1** — what constitutes hammer pass; mock/stub ceiling | migration authorization; every DB hammer's meaning | before hammer-matrix v0.2 acceptance (DB-4) |
| **OR-B2** — which hammers hard-gate which gate | migration authorization | with OR-B1 |
| **OR-C2** — retention posture per source family | raw-support physical schema | before schema spec covers raw support (DB-3) |
| **OR-C4** — raw archive layout | raw-support physical schema; backup posture | with OR-C2 |
| **New ruling: data-contract freeze acceptance** (N-03) | physical schema specification | DB-2 exit |
| **New ruling: database operational boundary** — local Postgres instance, roles, credential custody, backup posture (extends M19 secret rulings) | database creation | DB-3 entry |
| Not blocking but adjacent: OR-G3 (new scope classes — freeze binds current three), OR-A2/A3 (AI sentiment/sample-summary — stay fail-closed; no schema), OR-C11 (recurrence — stays rejected; §18) | — | — |

---

## 22. Minimum Pre-Database Correction Set

## What Must Be True Before The First Real Migration

The dependency-aware correction order. Steps 1–2 are corrections to the accepted v1; steps 3–7 are the entry conditions the first migration must find already true.

```text
Step 1  (documentation truth; hours)
        N-05: delete phase restatements from README.md and LLM_START_HERE.md
              (pointers only, per the rule LLM_START_HERE already contains);
        N-09: amend typed-read contract §24 (Hermes lineage resolved) with change-log entry;
        note in hammers/README that the gate policy is draft pending OR-B1/B2.

Step 2  (contract + prototype integrity; days)
        N-01: contract §15 disclosure amendment + prototype fix + over-ceiling
              adversarial fixture; N-08: cursor expiry (contract already requires it);
        N-13: promotion-flag computation + fixture; N-11: authorization-composition rule.
        These are v0.1→v0.1.1 contract corrections, not new scope.

Step 3  (rulings; owner sessions)
        OR-B1 + OR-B2 (database-phase hammer gate policy);
        OR-C2 + OR-C4 (retention posture + raw layout);
        hammer-matrix/acceptance-policy promoted from draft to accepted v0.2
        absorbing the §11 database hammer program;
        per-hammer result-register format extension.

Step 4  (data-contract freeze — the DB-2 milestone)
        N-03: one consolidated, owner-accepted logical data contract
        (§10 matrix as seed; reconcile capture_method/instrument delta,
        freshness/status vocabularies, scope-class binding, ID minting spec,
        forbidden-persistence list carried verbatim).

Step 5  (operational boundary)
        Local Postgres boundary ruling: instance custody, three DB roles
        (migrate / ingest / read-only), credential custody under M19 secret
        posture, backup-before-migration rule, containerized-PG CI harness.

Step 6  (harness before schema)
        Database hammer harness able to run DB-A/B/C/E series against an
        empty schema candidate — the harness exists BEFORE the first
        migration so migration #1 is born gated.

Step 7  (only then)
        First migration authorized, executed under DB-E1/E6.
```

## What I Would Fix Before Allowing One Real Observation Into Postgres

Distinct from the migration gate — synthetic evidence may flow at step 7; *real* evidence (provider-captured or manual-public) requires everything above **plus**:

1. **The N-04 enforcement substrate, built and hammered** — decision-linked authority record, committed ledger as duplicate substrate with closed lifecycle and locking, cumulative + post-receipt spend enforcement, preflight in the durable package, fresh-clone paid-request rejection hammer passing. The provider machine stays off until its cage is structural.
2. **Idempotent ingestion proven under concurrency** (DB-D1–D3): the duplicate key that protected $0.002 must protect the database's historical integrity.
3. **Encrypted, off-machine backup generation verified** (N-07 resolved) plus the semantic restore proof (§19 item 3): real evidence that exists in one place on one disk is not yet evidence.
4. **Canonical shape fingerprint implemented** (F-12 gate) and unknown-family quarantine live, so the second-ever real payload becomes drift evidence instead of silent variance.
5. **OR-C2's posture applied to the specific family being ingested** — no real observation enters under an unruled retention class.
6. **The silent-partial-view hammer (DB-C7) passing over a population larger than every ceiling** — the read layer must be proven honest about what it withholds before real evidence depends on it.
7. **A new, explicit, request-specific owner decision for the capture itself** — carried forward unchanged from the M13 closure's own rule.

---

## 23. Recommended Database-Phase Milestone Sequence

## How To Build The Database Without Letting It Become The Astronomer

The sequence below is dependency-aware and deliberately keeps the five permission gates the directive distinguishes (plan schema / write migration specs / create local DB / execute migrations / ingest real evidence) as separate owner decisions. The anti-astronomer discipline is baked in structurally: interpretation-shaped persistence is on a forbidden list the freeze carries verbatim; every migration diffs against that list; OR-A1's compute-on-read ruling is enforced as an *absence of schema*; derived read models (freshness, disagreement, coverage, claim fitness) are computed, never stored; and the only new stored things the whole phase creates are observations, provenance, vocabularies, manifests, and audit events — the telescope's parts list, nothing from the astronomer's notebook.

**DB-1 — Post-v1 Audit Reconciliation and Ruling Closure.**
Purpose: consume this audit; close OR-B1/B2/C2/C4; apply Steps 1–2 corrections. Inputs: this report, tracker, hammer drafts. Allowed: documentation/contract corrections, ruling proposals, decisions. Forbidden: schema, Postgres, migrations, code beyond the N-01/N-08/N-11/N-13 fixes. Exit: all Step 1–3 items closed with decisions. Owner gate: ruling acceptances. Hammer gate: N-01 adversarial test green.

**DB-2 — Physical Data-Contract Freeze.**
Purpose: the single consolidated logical contract (N-03). Inputs: §10 matrix, all accepted contracts, fixture models, M10 plan, C00 committed evidence. Allowed: consolidation, reconciliation, classification, ID-minting spec. Forbidden: DDL, table drawings beyond responsibility level, new capabilities. Exit: owner-accepted freeze; forbidden-persistence list embedded. Owner gate: freeze acceptance. Hammer gate: none (planning).

**DB-3 — Postgres Operational Boundary + Physical Schema Specification.**
Purpose: operational ruling (instance, three roles, credential custody, backup rule) and the schema spec derived solely from the freeze — tables, constraints, indexes, privileges, append-only mechanics, vocabulary tables — as specification, not DDL execution. Allowed: spec documents, migration *specifications* with rollback pairs. Forbidden: creating the database, running anything, provider work. Exit: spec accepted; every elevated-risk rule (§9) has a named physical mechanism. Owner gates: operational ruling; schema-spec acceptance (= permission to write migration specs, distinct from executing them).

**DB-4 — Database Hammer Harness.**
Purpose: containerized-Postgres harness implementing §11 A/B/C/E series against the schema spec's candidate DDL in disposable databases; per-hammer register live. Allowed: harness + hammer code, disposable DBs in CI/local. Forbidden: the durable local database, ingestion, read exposure. Exit: harness executes; migration-pair hammers (DB-E1/E2/E3) demonstrably able to fail. Owner gate: hammer-matrix v0.2 + OR-B1/B2 already accepted (DB-1). Hammer gate: harness self-proof.

**DB-5 — Local Database Bootstrap + First Migrations.**
Purpose: create the governed local database; execute migration #1..n under the harness; roles and privileges proven (DB-F3, DB-C6). Forbidden: any real or synthetic evidence beyond harness fixtures; network exposure. Exit: schema live; all migration-acceptance hammers pass; backup-before-migration executed. Owner gate: **migration execution authorization** (the separate gate). Hammer gate: DB-A1/A4/A6, DB-B1, DB-C1/C2/C5/C6, DB-E1–E4 pass.

**DB-6 — First Persisted Synthetic Evidence Slice + Database-Backed Typed Read.**
Purpose: persist the C2-family synthetic slice through the real write path (admission, audit-first, evidence identity); stand up the minimum DB-backed read slice (§14) on the read-only role. Forbidden: real evidence, providers, MCP/network, consumers beyond internal callers. Exit: DB-D2/D4 (concurrency on the write path), DB-F1–F8, DB-C7, DB-B2 pass; typed-read result register gains its first `real_surface_executable` entries. Owner gate: synthetic-slice authorization. Hammer gate: the read-slice set.

**DB-7 — Database Backup, Restore, and Recovery Proof.**
Purpose: §19 requirements — dump/restore with semantic verification, backup-before-migration proven in anger, first encrypted off-machine generation (resolving N-07). Exit: DB-E5/E6 pass; recovery register entry. Owner gate: backup posture + key custody. Hammer gate: DB-E6.

**DB-8 — Provider Enforcement Substrate + First Persisted Controlled Real Observation.**
Purpose: build N-04 (authority record, ledger enforcement, budgets, lifecycle, preflight persistence, fresh-clone hammer); then one owner-authorized real capture ingested idempotently under OR-C2's posture, with canonical fingerprint and unknown-family quarantine live. Forbidden: recurring capture, additional endpoints beyond the authorized recipe, customer anything. Exit: one real observation persisted, hammered (DB-D1/D3/D6, DB-B3/B5, DB-C4), and readable with full caveats. Owner gates: substrate acceptance + a new request-specific capture decision. Hammer gate: full ingestion set.

**DB-9 — Operational Acceptance (Database v1).**
Purpose: review every per-hammer register entry, every open ruling, every deferred boundary; accept the database at its own bounded ceiling (local, single-operator, non-production, no consumers beyond internal callers). Exit: acceptance decision mirroring M20's honesty. Owner gate: acceptance. Everything beyond — production API/MCP, consumer network access, recurrence, additional providers, real overlays — remains gated behind its own future decisions, exactly as today.

---

## 24. Known Limits That Must Remain Visible

Carried forward from the accepted register, unchanged and endorsed: local/bounded; no live persistence (until DB-5+); provider ceiling (one C00 recipe, narrowly validated); typed-read ceiling (fixture prototype until DB-6); consumer ceiling (proof workflow, not report generation); overlay ceiling (code-path only; infrastructure guarantees unproven); recovery ceiling (repository only; encryption blocked); recurrence rejected. Added by this audit and to remain visible alongside them: the hammer gate policy is a draft pending OR-B1/B2 (N-02); the read layer's ceiling-disclosure behavior is defective until N-01 lands; the enforcement substrate for provider work is unbuilt (N-04); the volatility vocabulary is honest placeholder (`moderate`/`unknown`) until repeated real samples exist; and no per-hammer H1–H22 execution record exists yet — suite passes are not hammer passes.

---

## 25. Dangerous-Capability Opportunities for the Database Phase

## How The Observatory Can Become Unusually Powerful Without Becoming A Strategy Engine

The prior audit's routing (O-7/O-8/O-9 active design inputs; O-1/O-2 future M16/M18-class; O-3/O-4 research candidates; O-5/O-6 rights-constrained; O-10 operations-maturity) was consumed properly and holds. What the *database* specifically adds is one thing the fixture era could not have: **time**. Every opportunity below is a shape of the same move — persist observations so honestly that longitudinal joins become possible, while interpretation stays compute-on-read. Classification per the directive:

| ID | Opportunity | Value | Required evidence | Database prerequisite | Rights risk | Retention risk | Cost risk | Scope risk | Consumer location | Timing |
|---|---|---|---|---|---|---|---|---|---|---|
| DB-O1 | **Historical observation replay / as-of reads** — reconstruct what the Observatory knew at any past instant | very high; makes Kaizen citations permanent and disputes resolvable; brutal to retrofit | any persisted evidence | append-only + status transitions timestamped (DB-5 schema decision — costs almost nothing if designed in) | none | none | none | none | read feature; interpretation downstream | design into DB-3 schema; expose at DB-6+ |
| DB-O2 | **Provider shape-drift histories** — canonical fingerprints per capture, diffed over time; the instrument's own biography | high; converts every future capture into drift science competitors don't keep | ≥2 real samples per recipe | fingerprint-per-capture table (append-only event) | none | low | per-sample capture cost | none | internal + provider-integration planning | schema at DB-3; data from DB-8 onward |
| DB-O3 | **SERP feature evolution / rare-feature archive** — item-family composition per capture; specimens of transient features preserved | high; longitudinal feature archaeology; nobody preserves dead SERP features | repeated captures | item-family typed storage (freeze decision) | low (provider-mediated) | OR-C2 per family | cadence-driven (M18 policy governs) | none | internal research; SearchClarity narratives assembled outside | after recurrence is separately authorized |
| DB-O4 | **Multi-provider disagreement histories** — persisted per-side testimony (never verdicts), disagreement computed on read across time | high; "where the tools disagree, with receipts, over months" | second provider/engine admission | per-side provider-attributed metrics with full context tuple (M16 shape) | per-provider terms | low | small | none | read output; conclusions promote out | after a second admission decision |
| DB-O5 | **Claim-safe absence histories** — sampled absence observations with sample-bound caveats accumulating into honest "not observed across N samples" statements | medium-high; the only honest version of "you're invisible on X" | repeated sampling per surface | absence observations as first-class rows (freeze) | low | low | sampling cost | none | SearchClarity language stays consumer-side | with repeated capture |
| DB-O6 | **Freshness-aware evidence packs over real corpus** — O-9 matured: volatility classes learned from persisted churn, caveats grounded in measurement | multiplier on everything | persisted time-series | DB-O2/O3 data + computed freshness | none | none | none | none | the read layer itself | grows automatically from DB-8 onward |
| DB-O7 | **Provider cost & evidence-yield analysis** — cost witnesses per capture joined to field-yield; "what a maintained scope actually costs" | medium-high; the unit-economics moat test (prior lane R3) | cost reconciliation rows (already modeled) | cost fields persisted per capture (C00 template) | none | none | none | none | internal planning; blind-spot cost facts in read output (O-7) | DB-8 onward |
| DB-O8 | **Rights-aware evidence reuse across consumers** — one observation, many scoped consumers, rights/retention labels enforcing who may see what | high commercial leverage; K2's separation realized physically | any shared evidence | scope + rights enforcement at role/read level (already required) | the whole point — enforced, not risked | enforced | none | the central design constraint | consumers each side of the boundary | inherent from DB-6 |

Anti-opportunity guardrails, restated for the phase: every mechanical derivation (feature diffs, recurrence counts, drift summaries) passes the V6 materialization test *in writing* before any table exists; anything that smells like a score, verdict, winner, or trend-conclusion is computed on read or promoted out; and the forbidden-persistence list in the freeze is the diff-target for every migration review. The moat remains the corpus and its honesty — the database phase just gives the corpus a spine.

---

## 26. Commercial Leverage Without Consumer Contamination

The future database can safely support every listed line of work, because the boundary architecture already proven at fixture level maps directly onto DB roles and scoped reads:

- **SearchClarity evidence packs / SEO-GEO audits:** disposition-classified packs (M15 shape) over real longitudinal evidence; report assembly, customer identity, and final claims stay SearchClarity-side; the only DB requirements are consumer-neutral (durable handles, status-aware reads, as-of). Highest near-revenue path; DB-O5 absence histories and DB-O4 disagreement receipts are its differentiated sections.
- **SERP visibility histories / competitive comparison:** market_watch scopes + DB-O1/O3; competitive intelligence is a read-time synthesis over observations of public surfaces — nothing competitor-specific is stored beyond the observations themselves.
- **Marketplace and video/YouTube visibility research:** remain behind their rights ceilings (OR-C5–C8; compliant manual capture; YouTube via provider recipes like the parked C03) — the database adds longitudinal value only after per-surface admission; no schema accommodation now.
- **AI citation research:** the highest-leverage research lane (prior O-3) — database prerequisite is the AI-surface families (V18/K6, distinct, never collapsed) entering the freeze as *deferred-owned* concepts, built only when OR-C3 admission and sampling rulings land.
- **Neon Ronin workspace research:** workspace-scoped read grants + the governed pull-request queue; queue state is Neon Ronin's, requests recorded as consumer job metadata (K2), observations stay clean and shared.
- **Future paid evidence products:** the rights-aware reuse capability (DB-O8) is the enabler — one rights-clean corpus, many scoped consumers — and it requires no consumer-specific persistence, which is the test every future feature must keep passing.

**High-value evidence competitors fail to preserve** (the database-phase shortlist): dated per-surface AI citation samples; SERP item-family composition over time (not just rank); provider disagreement pairs with full context tuples; transient/rare SERP feature specimens; provider drift fingerprints; honest sampled-absence series; cost-per-evidence-yield records. **Database features that are real leverage vs. theater:** as-of reads, append-only with supersession, per-side attribution completeness, and role-enforced boundaries are leverage; anything resembling scores-as-columns, trend tables, disagreement verdicts, or consumer-specific fields is theater at best and contamination at worst.

---

## 27. Final v1 Verdict

```text
PASS WITH REQUIRED CORRECTIONS
```

The v1 acceptance was justified, its language matched its proof, its limits register is honest, and my independent execution confirms its central factual claims. Required corrections, none of which disturb the acceptance: N-05 (stale README/LLM_START_HERE phase restatements — remove restatements, not just refresh values), N-09 (accepted contract §24 asserts a resolved gap), and an explicit note that the hammer gate policy remains draft pending OR-B1/B2 so "hammer tests are a hard gate" cannot be read as an accepted definition (N-02's documentation face).

---

## 28. Final Database-Phase Readiness Verdict

```text
CONDITIONAL GO — physical planning may begin now.
```

By the directive's separated gates:

| Gate | Verdict | Condition |
|---|---|---|
| Permission to plan physical schema | **GO** | begin with DB-1/DB-2 (audit reconciliation + data-contract freeze); N-05/N-09/N-01 corrections land in DB-1 |
| Permission to write migration specifications | CONDITIONAL | after the freeze (N-03) and the operational-boundary ruling; OR-C2/C4 required before raw-support specs |
| Permission to create a local database | CONDITIONAL | after schema-spec acceptance and the hammer harness exists (DB-4) — the harness precedes the database |
| Permission to execute migrations | **BLOCKED until** | OR-B1/OR-B2 ruled, hammer-matrix v0.2 accepted, per-hammer register live, backup-before-migration in force (N-02) |
| Permission to ingest real provider evidence | **BLOCKED until** | the N-04 enforcement substrate is built and hammered, encrypted off-machine backup exists (N-07), canonical fingerprint + quarantine live (F-12), OR-C2 applied to the family, and a new request-specific owner decision exists |
| Permission to expose database-backed read tools | **BLOCKED until** | DB-6 read-slice hammers pass, including DB-C7 (the N-01 class) over an over-ceiling population |
| Permission to operate in production | **BLOCKED** | outside this phase entirely; requires its own future roadmap and acceptance |

The project earned this phase. The prior audit ended by saying the telescope's optics were good and the doors needed to lock from inside the decisions; v1 locked every door that mattered and labeled every one it left for later. What the database phase must now add is the part no fixture can fake: a substrate that enforces the doctrine when nobody is looking, hammers that are allowed to fail, and the patience to let one synthetic slice, one backup proof, and one real observation each earn their own gate. The goal, as the directive says, is not to prevent the next phase — it is to make sure the database that emerges is worthy of the doctrine that has, so far, been kept.

---

*This report is advisory source material only. It is not accepted doctrine, an owner ruling, schema approval, migration approval, database-creation approval, provider admission, implementation authority, or production authority. Per `audits/README.md`, any document citing this audit as authority for a capability is invalid by construction.*
