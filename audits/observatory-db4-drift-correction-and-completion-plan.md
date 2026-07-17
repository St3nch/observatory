# The Observatory — DB-4 Drift Correction and Completion Plan

Purpose of this document: take the project from its current honest-but-incomplete state to a DB-4 that can close on real evidence, without losing the doctrine that makes the Observatory worth building. Advisory only. Authorizes nothing.

---

## 0. Anchor: what this project is, and what "best" means for it

Before any task list, the north star, because every decision below serves it:

- The Observatory is a **telescope**. It stores what was observed — provenance-complete, append-only, rights/retention-governed evidence. The connected LLM is the **astronomer**; interpretation happens at read time and promotes *out*, never *in*.
- "Best" for this project is **not** more features. It is *trustworthiness*: a database whose structure makes evidence corruption and boundary violation harder than honest storage, and whose proof is harder to exaggerate than to record honestly. That sentence is already in your own docs. The whole DB phase exists to make the doctrine *mechanical*, not rhetorical.
- Therefore the measure of DB-4 is not "does it run" but "does every boundary have a hammer that can fail, and did that hammer actually fail when we broke the mechanism." A green suite that tests toy tables is worth less than one red hammer that tests the real spine.

The drift you noticed matters precisely because it is the failure mode the whole project is built to resist: **paperwork that looks like proof.** Fifteen named hostile candidates absent, surrogate probes standing in for the real spine, a manifest that reads as satisfied when it is not. None of it is catastrophic. All of it is the exact thing the Observatory is supposed to make impossible for *itself*.

So the goal of this plan is not just "add the missing files." It is: **restore the property that the repository cannot quietly overstate its own completeness.**

---

## 1. Diagnosis: name the drift precisely

Four distinct drifts, in priority order. Treat them as different problems — they have different fixes.

**D1 — Silent incompleteness (governance drift).** The remediation manifest names 23 hostile fixtures and 11 postgres tests. The repo has 8 and 5. Nothing records that the other 15 + 6 are missing. The manifest reads as done. This is the most dangerous drift because it is *invisible* — a future steward or coding agent reads "accepted remediation package," sees green, and proceeds. Fix class: make incompleteness impossible to carry silently.

**D2 — Proof-substrate drift (the core technical drift).** The remapping doc's law — "no control-plane probe table substitutes for project relations" — is violated by migration 010's `obs_meta.db4_*` surrogate probes for H2/H3/H5/H19/H20. The real mechanisms exist (admission trigger, unique mints, append-only triggers, audit-first constraint triggers) and the real two-scope seed exists, so the surrogates are *unnecessary* as well as non-conforming. Fix class: rewire behavioral checks to the real spine; delete the surrogates.

**D3 — Retained-not-redesigned drift.** Seven of eight kept fixtures are byte-identical bare tables; the plan said "retain and redesign as real admission-path candidates." Only `schema_version_divergence` was redesigned. Fix class: redesign the seven, and decide honestly which hostile candidates are PostgreSQL-rejected (self-proving) vs runner-detected (detector-dependent).

**D4 — Coverage-gap drift (surfaced by D1's missing fixtures).** The two absent fixtures `009_owner_bypass_rls` and `009_rls_without_force` are exactly the sabotage cases that would have caught the real RLS-child-table hole (backup role reads cross-scope evidence identities). The missing fixtures aren't just unbuilt tests — their absence *let a real schema hole survive*. Fix class: the RLS gap is a schema defect to fix now, and its absent hammer proves the fixtures aren't optional.

The through-line: **D1 caused D4.** When you stop requiring the hostile candidates, you stop finding the holes. That is the argument for fixing the governance drift first.

---

## 2. Strategic choice: three honest routes, and the one I recommend

You asked for the *best* route, not the fastest. Here are the real options.

**Route A — "Conform to the manifest exactly."** Build all 15 fixtures, all 6 tests, rename rollbacks to `.down.sql`, rewire every probe, then run. Maximally faithful. Risk: it treats the manifest as gospel, but the manifest itself was written *before* the schema existed and may over-specify (e.g. some of the 15 fixtures overlap; a few may be better as behavioral checks than as loose SQL files). Blindly conforming re-introduces the "file presence = done" thinking you're trying to escape.

**Route B — "Amend the manifest to match what was built, then close."** Fastest. Deeply wrong for this project. It ratifies drift as the norm and trains the next agent that manifests are negotiable after the fact. Rejected.

**Route C — "Reconcile: make one honest, current, gap-aware manifest; then complete against it."** Neither worship the old manifest nor quietly abandon it. Produce a single reconciliation decision that (a) records exactly what was built, what is missing, and what the old manifest over- or under-specified; (b) re-derives the *required* hostile-candidate and test set from first principles (the hammer matrix + DB-3 responsibilities), not from the old list's momentum; (c) fixes the real schema holes; (d) then completes. This is slower than A by a little and produces a repository whose completeness claims are true again.

**Recommendation: Route C.** It is the only route that fixes D1 (the governance drift) rather than just its symptoms. The others fix files; C fixes the property that lets files drift.

---

## 3. The plan: five bounded batches, sequenced

Each batch has a stop condition and a "does this change doctrine" flag (none should). Batches are ordered so that governance is restored *before* more code is written — otherwise you are pouring new work into a leaky manifest.

### Batch R0 — Reconciliation and honest baseline (governance first)
**Goal:** the repository stops overstating its own completeness. No SQL yet.
- Produce a **reconciliation decision** (`decisions/YYYY-MM-DD-db4-remediation-reconciliation.md`) that states plainly: schema rebuild (I3) substantially complete; behavioral profiles present; **hostile-candidate set 8/23 built, 15 named-but-absent (list them)**; **postgres test set 5/11, and the 5 present are the stale relics the plan said to replace**; rollback naming deviates; surrogate probes violate the no-substitute rule.
- Make a **first-principles decision** for each of the 15 absent fixtures: *required*, *fold-into-behavioral-check*, or *explicitly-deferred-with-reason*. Do not carry any of them silently. `owner_bypass_rls` and `rls_without_force` are **required** (they guard a real hole).
- Add a **manifest-conformance check** to `tools/check_database_package.py`: the validator reads the accepted fixture/test/profile manifest and **fails if a named artifact is absent** or an unnamed one appears. This is the mechanical fix for D1 — after this, silent incompleteness is impossible; the suite goes red the moment reality and manifest diverge.
- **Stop condition:** reconciliation decision committed; conformance check fails loudly against the current gap (proving it works) until the gap is closed by later batches, or the deferrals are recorded so it passes honestly.
- **Doctrine change:** no. This *enforces* existing doctrine.

### Batch R1 — Fix the real schema holes the missing hammers would have caught
**Goal:** close defects, not just add tests for them.
- **RLS child-table coverage:** enable `FORCE ROW LEVEL SECURITY` + scope-derived policies on the unprotected scope-bound children (`obs_evidence.evidence_identity`, `citation_handle`, `admission_transition`, `observation_transition`, `observed_artifact_reference`; `obs_raw.raw_payload_identity`, `opaque_artifact_token`, `raw_integrity_observation`) **or** remove base-table `SELECT` from `observatory_test_backup`/`migrator` and route them through `obs_read`. Prefer the former for defence in depth.
- **Append-only escape:** re-anchor `reject_mutation`'s cleanup exception to named key columns with a `db4-` prefix, not `'%db4-%'` in full row text.
- **UUID-vs-text-PK:** reconcile the traceability matrix's "internal UUID PK" law with the delivered text-natural-key design (pick one; I lean toward amending the matrix — the text keys are clean and self-documenting — but it must be a recorded choice).
- **Stop condition:** these live in migrations 001/007/010; changes are within the accepted migration responsibilities; validator green.
- **Doctrine change:** no.

### Batch R2 — Rewire behavioral proof to the real spine (kill the surrogates)
**Goal:** every mandatory hammer exercises the real relation, satisfying the remapping law.
- Rebuild the H2/H3/H5/H19/H20 probe paths to use the **real** seed corpus (`db4_seed_role_rls_probe` already builds two real scopes): H2/H3 attempt a real `obs_evidence.observation` insert with missing rights/retention → expect the admission trigger's `23514`; H5 duplicate real `evidence_identity` → `23505`; H19 UPDATE/DELETE a real protected relation → `42501`; H20 race two real identity mints with forced overlap → exactly one `23505`.
- Delete the `obs_meta.db4_*` surrogate tables and their probe functions (they become dead weight once the real paths are wired).
- Keep the advisory-lock migration-serialization probe (it is real) but move its identity-mint sibling onto the real mint.
- **Stop condition:** no `obs_meta.db4_*` surrogate remains that stands in for a project relation; each behavioral check names a real relation and an expected SQLSTATE; validator green.
- **Doctrine change:** no.

### Batch R3 — Complete the hostile-candidate set (the 15), redesigned correctly
**Goal:** the broken-candidate campaign actually proves the harness rejects bad schema.
- Build the *required* fixtures from R0's triage. For each, decide and record its **rejection point**: PostgreSQL-native (like `schema_version_divergence` hitting the real CHECK — preferred, self-proving) vs runner-detected (name/structure based — weaker, ob-dev-dependent). Push as many as possible to PostgreSQL-native so the proof does not lean on the frozen ob-dev.
- Redesign the seven retained bare-table fixtures the same way.
- Each fixture gets its manifest row (violated invariant, rejection point, SQLSTATE, rollback state, history state, cleanup) — the validator (R0) now enforces the row exists.
- **Stop condition:** conformance check green because every named fixture exists or is explicitly deferred with reason; every fixture has a rejection point classified native-vs-runner.
- **Doctrine change:** no.

### Batch R4 — Complete and de-stale the test layer
**Goal:** the green suite tests the current design, not relics.
- Delete the five dead `db4_*_v1.json` profiles and rewrite/remove the five stale `tests/postgres/test_db4_*.py` that load them.
- Add the six planned-but-absent postgres tests (`history_atomicity`, `result_register`, `security_posture`, `cleanup`, `profile_manifest`, `broken_candidate_manifest`) — as *contract/manifest* tests where they gate static properties, clearly labelled as not-yet-behavioral where they await the live run.
- **Stop condition:** no test loads a retired profile; suite green; conformance check green.
- **Doctrine change:** no.

### Batch R5 — Prepare (not run) the live disposable campaign gate
**Goal:** everything static is true; hand a clean, honest package to the owner-gated live run.
- Confirm the ob-dev freeze is compatible: list exactly which behaviors the live run needs from ob-dev (atomic DDL+history, real fingerprint, profile load by path+SHA, SET ROLE execution, record emission, marker/authority enforcement). If the frozen ob-dev already does these, note it; if any is absent, that becomes a *separate, explicitly-scoped* ob-dev decision — do not fold it into Observatory work.
- Draft the live-campaign owner decision (the I10 gate) with the §27 checklist from the audit as its acceptance criteria.
- **Stop condition:** a single decision doc that, when the owner accepts it, authorizes one disposable campaign that emits reviewable records.
- **Doctrine change:** no. This is the boundary where DB-4 proof becomes real; it stays owner-gated.

---

## 4. Sequencing rationale (why this order is the best route)

- **R0 before everything** because the governance fix is what stops the next drift. If you build fixtures first and add the conformance check later, you've fixed today's gap but not tomorrow's.
- **R1 before R2/R3** because the RLS hole is a live defect; fixing schema before writing hammers against it means the hammers test the fixed reality.
- **R2 before R3** because once the real spine is wired for behavioral checks, several "missing fixtures" may be better expressed as behavioral checks (fold, not build) — you avoid building loose SQL you'll then delete.
- **R4 after R2/R3** because the tests should target the final profiles/fixtures.
- **R5 last and owner-gated** — the live run is the only thing that converts intended `real_postgres_disposable_pass` into achieved. Nothing before it may claim closure.

## 5. What "done" looks like (closure criteria — unchanged from doctrine)

DB-4 closes only when **both**:
1. every static finding above is resolved and the conformance check makes the manifest honest; **and**
2. a separately-authorized disposable campaign has run on a clean marked substrate and emitted reviewable immutable records showing: real-spine behavioral hammers pass under `SET ROLE`; each sabotage makes its hammer fail; all hostile candidates rejected with no residue; cross-scope denied for every role including backup; atomic DDL+history; clean reverse rollback and disposable drop.

Static work alone never closes DB-4. That rule is the project's spine; keep it.

## 6. Guardrails so this plan doesn't itself drift

- **One reconciliation decision, then work against it** — no side-quests, no unmanifested files.
- **The conformance check is the ratchet** — once R0 lands, the repo cannot silently overstate completeness again. This is the single most valuable artifact in the whole plan; it is worth more than any individual fixture.
- **ob-dev stays frozen unless a named, separate decision changes it** — respect the owner's hard-won stability there; never fold ob-dev changes into Observatory batches.
- **Prefer PostgreSQL-native rejection over runner-detection** everywhere possible, so proof strength does not depend on the frozen control plane.
- **No new capability, no DB-5, no governed database, no providers** — this plan is entirely about making DB-4's existing scope honest and real.

---

## 7. One-paragraph summary for the next session

The schema rebuild is genuinely good and doctrine-faithful; the drift is that the hostile-proof half of the accepted manifest (15 of 23 fixtures, 6 of 11 tests) was left unbuilt *silently*, surrogate probe tables stand in for the real evidence spine against the project's own rule, and a real RLS hole survived because its guarding hammer was one of the absent fixtures. The best route is not to rush-conform to the old list but to (R0) record an honest reconciliation and add a validator conformance check that makes silent incompleteness impossible, then (R1) fix the real schema holes, (R2) rewire behavioral hammers onto the real spine and delete the surrogates, (R3) build/redesign the hostile candidates preferring PostgreSQL-native rejection, (R4) de-stale and complete the tests, and (R5) hand a clean, owner-gated package to the one live disposable campaign that alone can earn closure. Keep ob-dev frozen; keep the rule that only real execution with reviewable records closes DB-4.
