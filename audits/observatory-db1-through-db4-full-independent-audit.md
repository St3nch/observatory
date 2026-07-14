# The Observatory — Full Independent Database-Phase Audit (DB-1 → current DB-4)

Date: 2026-07-14
Auditor: Claude (independent read-only audit; filesystem MCP inspection of live working trees)
Method: adversarial claim-by-claim verification against source files, Git reflog, migrations, hammer code, fixtures, profiles, validators, and tests. No file in either repository was created, edited, staged, committed, or executed. No PostgreSQL command was run. The protected file `audits/kaizen_to_slash_goal_prompt.md` was not read (its existence in the directory listing was unavoidable and is noted only as an untracked-file expectation).

Audit limitation disclosed up front: without Git plumbing tools I could not compute `git status`/`git diff` directly. HEAD identities were read from `.git/refs` and `.git/logs/HEAD`. Working-tree-vs-HEAD deltas (including the possible uncommitted `postgres_hammers.py` change) could not be byte-diffed; per instructions, the **live working tree was treated as the audit evidence**. File mtimes confirm `src/ob_dev/postgres_hammers.py` was modified today after the last commit timestamp, consistent with the described uncommitted detector work.

---

## 1. Executive verdict

| Question | Verdict |
|---|---|
| Is DB-1 trustworthy? | **yes with conditions** |
| Is DB-2 trustworthy? | **yes with conditions** |
| Is DB-3 trustworthy? | **yes with conditions** |
| Is DB-4 ready to close? | **no** |
| Is DB-5 safe to authorize? | **no** |

**DB-1 — yes with conditions.** The hammer matrix v0.2, acceptance-gate policy v0.2, and per-hammer result-register contract v0.1 are coherent, internally consistent, and genuinely strong policy artifacts. The condition: the stale-authority regression the project already knows about has recurred again (`decisions/README.md` Last Review Notes still say the DB-4 package "remains unapproved" while the same file indexes the acceptance decision). DB-1's policy is trustworthy; the project's ability to keep restated authority synchronized is not yet.

**DB-2 — yes with conditions.** The freeze v0.2.1 is SHA-bound, immutably referenced, and cleanly distinguished from the retired lineage. Condition: this audit verified DB-2's governance chain, indexing, and downstream consumption (via the DB-3 traceability references), not every line of the freeze itself; nothing found contradicts it, but the DB-4 implementation shows DB-2 concepts (rights/retention assignments, candidate/admission lifecycle, transitions) are **not represented** in the delivered physical schema — a DB-4 fidelity problem, not a DB-2 defect.

**DB-3 — yes with conditions.** The DB-3 design specification is the strongest document in the database phase: forced-RLS, marker-bound identity, functional role model, append-only history, before/after fingerprints, advisory-locking-class concurrency requirements are all specified. Condition: DB-3's requirements were demonstrably **not carried into the DB-4 implementation** (see F-04, F-05, F-06, F-09, F-12). The spec is trustworthy; its enforcement is not yet real.

**DB-4 — no, not ready to close.** Under the project's own accepted gate (`acceptance-gate-policy-v0-2.md` §DB-4), closure requires: real-disposable passing hammers for the mandatory families, broken candidates shown failing, **and result-register entries that are complete and reviewable**. Today: (a) zero result-register records exist anywhere in the repository (`hammers/results/` absent, `.database-proof/` absent, profile `proof_output` files never written by any code path); (b) the hammer implementation predominantly catalogs structure under mislabeled hammer IDs rather than proving hostile claims; (c) the implemented tool registry (30 PostgreSQL tools / 62 total) exceeds the accepted exact 28/60 registry with no revised owner gate; (d) migration history is mutable and non-atomic, directly violating the accepted transaction rules. By the project's own standard — "Do not give credit for real PostgreSQL output that lacks durable reviewable result records" — the claimed DB-4 proof is currently **unproven**, independent of whether the terminal output was real.

**DB-5 — no.** DB-5 requires an accepted migration set proven under real hammers. The delivered migration set is a skeletal stand-in for the accepted DB-3 physical design; even a fully green DB-4 run over it would prove a toy schema. Authorizing DB-5 now would bootstrap a governed database from candidates that do not implement the accepted contract.

---

## 2. Repository truth snapshot

| Item | Value |
|---|---|
| Observatory HEAD | `6758f42378845d6706a8fef050c24ecd766b68f5` — "Add DB-4 migration and hammer package" |
| Observatory branch | `main` (per `.git/HEAD`) |
| Observatory working tree | Untracked protected file `audits/kaizen_to_slash_goal_prompt.md` present as expected (not read). No other working-tree delta was verifiable without git tooling; file mtimes show no post-commit edits to `database/`, `tools/`, or `tests/postgres/`. |
| ob-dev HEAD | `9a5cd53117622745ae68f2651ce23c988359d854` — "Use PostgreSQL ACLs for privilege fixture" |
| ob-dev remote | none (matches expectations) |
| ob-dev working tree | `src/ob_dev/postgres_hammers.py` mtime postdates the HEAD commit time → consistent with an uncommitted detector change. Live file audited as evidence. Notably, the live `009_excess_role_privilege` detector uses `aclexplode(...) ... a.grantee=0` with `count(*) > 0` semantics via `detector_count > 0` — the exact-count assumption has already been replaced by a threshold in the live tree. |
| Active authority | `decisions/2026-07-14-db4-package-acceptance-and-phased-implementation-authorization.md` (OR-J1/J2/J3). ACTIVE_CONTEXT, NEXT_SESSION_HANDOFF, ROADMAP, POST_V1_DATABASE_ROADMAP, and planning-inbox/README all agree. |
| Active milestone | DB-4 (implementation phase; not closed). DB-5 inactive. |
| Database inventory | Not directly verifiable (no PostgreSQL execution performed). Repository and prompt state claim `observatory_test_db4` was created, proven, and dropped. **No durable repository record confirms creation, proof, or drop.** |
| Role inventory | Not directly verifiable. `postgres_drop_bounded_test_roles` exists in code; the prompt states cleanup "may not yet have been executed." If not executed, `observatory_test_read` / `observatory_test_write` are **cluster-global residue** that survived the database drop. Must be verified and recorded before closure (F-18). |
| Disposable proof state | `.database-proof/` (Observatory) and `.postgres-proof/` (ob-dev) do not exist. No hammer result registers exist. All claimed proof is currently ephemeral chat/tool-output history. |
| Secrets check | No credentials, connection strings, or password material found in any inspected file. `settings.py` reads only the password env-var name; sanitization exists (with gaps, F-16). |

**Governance-history separation (retired vs. current):** The reflog cleanly shows the recovery arc: `restore DB-1 trust boundary` → `retire untrusted DB-3 and DB-4 artifacts` → fresh DB-2 acceptance → fresh DB-3 → DB-4 package → DB-4 authorization. `planning-inbox/README.md` labels every superseded/invalidated artifact explicitly, and the retired five artifacts are absent. This part of the repository is genuinely well-governed; a future agent following the read path would not reactivate retired work. One residual ambiguity: `POST_V1_DATABASE_ROADMAP.md`'s DB-4 section still carries "Active only for exact implementation-package preparation" prose and "Forbidden now: ob_dev source implementation / PostgreSQL tool registration / migration execution…" from the package-preparation era, while its own "Current state" block says implementation is authorized. A literal-minded agent reading only the milestone section would conclude the executed implementation was forbidden (F-11b).

---

## 3. Findings register

Severity: Critical / High / Medium / Low / Advisory. Timing codes: **C4** = must fix before DB-4 closure; **C5** = before DB-5 authorization; **GOV** = before governed database creation; **PROV** = before provider admission; **PROD** = before production; **DEF** = safe to defer.

### F-01 — No durable proof records exist for any claimed DB-4 execution
- **Severity/Timing:** Critical / C4. **Category:** proof defect + governance defect.
- **Affected:** `hammers/per-hammer-result-register-v0-1.md`, `hammers/acceptance-gate-policy-v0-2.md`, `database/hammer-profiles/*.json` (`proof_output` fields), absent `hammers/results/`, absent `.database-proof/`, all of `ob_dev/postgres_hammers.py`.
- **Requirement:** DB-4 closes only with "result-register entries [that] are complete and reviewable"; each execution produces one immutable record with commit SHA, migration SHAs, evidence paths, review status.
- **Observed:** No code path in ob-dev writes any proof artifact. The profile JSONs name `proof_output: "db4/invariants.json"` etc., but nothing reads or writes them. The proof roots do not exist. The only DB-4 "evidence" is transient MCP tool output in chat history.
- **Why it matters / failure scenario:** The project's core anti-proof-inflation control is the register. Right now a future steward must either take chat history on faith or re-run everything. The claimed "9 migrations, 12 core assertions, 3+3+3 assertions, race, 9 rollbacks, drop" is — by the project's own definition — *not proven*.
- **Correction:** Implement register emission in ob-dev (append-only YAML per `result_record_version 0.1`, written under the ignored proof root, then a redacted reviewed copy committed under `hammers/results/DB-4/`). Re-execute the disposable campaign to generate real records. Add the planned register validator.
- **Validation:** Register validator passes; each mandatory DB-4 hammer family has a reviewable record at `real_postgres_disposable_pass`.

### F-02 — Implemented tool registry exceeds the accepted exact 28/60 registry
- **Severity/Timing:** Critical / C4. **Category:** governance defect.
- **Affected:** `ob-dev/src/ob_dev/server.py`, `tests/test_server.py`, `ob-dev/README.md`, accepted `db4-exact-ob-dev-implementation-package-specification.md`, OR-J2.
- **Requirement:** "exact 28 PostgreSQL tools, producing the expected 60-tool registry… Any required path/tool outside the manifest blocks implementation and requires a revised owner gate." ACTIVE_CONTEXT stop condition: "unexpected tool or tool-count mismatch."
- **Observed:** Live registry contains **30** PostgreSQL tools (62 total): `postgres_drop_bounded_test_roles` and `postgres_run_broken_candidate_profile` are not in the accepted registry. They were added by commits `c3ee6420…` ("Add broken-candidate proof and role cleanup") with **no decision record** in `decisions/` after the DB-4 acceptance. `tests/test_server.py` was rewritten to assert the 62-tool surface — the test now mirrors the implementation instead of the accepted contract. `ob-dev/README.md` still claims "exactly 28" — the README, tests, and code disagree three ways.
- **Why it matters:** Both added tools are *good ideas* (cleanup and broken-candidate proof were required capabilities), but the entire DB-4 control model rests on "tool existence never widens authority" and "stop on tool-count mismatch." The precedent — steward adds mutation-class tools mid-campaign and adjusts the guard test to match — is exactly the failure mode the exact-manifest regime exists to prevent.
- **Correction:** Owner ruling that retroactively accepts or rejects the two tools by name, amends the registry to 30/62 (or removes them), and records the deviation. Restore the contract-first posture of `test_server.py` by deriving `EXPECTED_TOOLS` from a committed accepted-registry document, not an inline set. Fix README.
- **Validation:** decisions record exists; README/tests/health/registry digest agree.

### F-03 — Hammer implementation catalogs structure under mislabeled hammer IDs; hostile claims are not exercised
- **Severity/Timing:** Critical / C4. **Category:** proof defect + test defect.
- **Affected:** `ob-dev/src/ob_dev/postgres_hammers.py` (`_PROFILE_CHECKS`), `hammers/hammer-matrix-v0-2.md`, `database/hammer-profiles/db4_invariants_v1.json`.
- **Requirement:** Matrix v0.2: H2 = rights fail-closed, H3 = retention enforcement, H5 = no strategy storage, H19 = append-only observations, H21 = audit-first same-transaction. DB-4 must prove these behaviorally on a real disposable substrate.
- **Observed (per-check):** code "H2" = *scope table exists*; "H3" = *count of FOREIGN KEY constraints in observatory_capture = 1*; "H5" = *count of UNIQUE constraints in observatory_evidence = 1*; "H19" = *schema_migration table exists*; "H21" = *restore_verification table exists*; "H12" = RLS flag set (H12 is raw-manifest integrity in the matrix); "H15" = policy row exists. **No check ever attempts a forbidden write and observes rejection.** The append-only trigger is never fired by an UPDATE/DELETE; RLS is never evaluated (see F-06); no rights/retention rejection is exercised; H4 (customer-private rejection) is absent entirely. The "H9"/"H18" IDs in code aren't even in the DB-4 mandatory family list.
- **Why it matters / counterexample:** A schema with the right table names but a broken trigger function (e.g., `reject_mutation()` redefined to `RETURN NEW`) passes every core hammer. A schema whose RLS policy is `USING (true)` passes H12/H15. This is proof inflation in code: catalog presence marked `real_postgres_disposable_pass` against hostile-claim IDs.
- **Correction:** Rebuild the hammer layer around *behavioral assertions with expected failures*: attempt `UPDATE observatory_audit.event …` → expect exception class; `SET ROLE` to a granted non-owner role and probe cross-scope invisibility under `FORCE ROW LEVEL SECURITY`; attempt duplicate `evidence_handle` insert → expect unique violation; attempt `UPDATE observatory_meta.schema_migration` → expect rejection (requires F-04 fix first). Re-key checks to matrix IDs honestly; anything that is a structural precondition should be labeled `structure-precheck`, not `H*`.
- **Validation:** Each mandatory DB-4 hammer family has at least one negative behavioral assertion that fails when the enforcement mechanism is deliberately broken (mutation-test the hammers themselves).

### F-04 — Migration history is mutable and non-atomic (split-brain by construction)
- **Severity/Timing:** High / C4. **Category:** implementation defect + design defect.
- **Affected:** `ob-dev/src/ob_dev/postgres_control.py::apply_migration_file`, `database/migrations/001_identity_namespaces.sql`.
- **Requirement:** Accepted transaction rules: "migration history is append-only"; "a failed candidate must not become an accepted migration-history row"; before/after fingerprints recorded; history effectively atomic with the migration.
- **Observed:** (1) History is inserted with `ON CONFLICT (version) DO UPDATE SET file_sha256=…, schema_fingerprint=…` — the history row for any version can be silently rewritten by re-applying. (2) History insertion is a **second psql process after the migration transaction has committed** — the migration can succeed while history recording fails (`migration_history_failed`), leaving applied-without-history state; conversely nothing prevents history rows without schema (the 009 fixture demonstrates that PostgreSQL happily accepts one). (3) No `before` fingerprint is recorded despite the spec requiring before/after. (4) Nothing protects `schema_migration` itself from UPDATE/DELETE (no trigger, no revoke) — the append-only claim about history is enforced nowhere.
- **Failure scenario:** Re-running migration 004 after editing its file quietly replaces the recorded SHA — the exact "history rewrite" attack the fixture list was supposed to catch, available through the front door.
- **Correction:** Make the migration file itself (or the runner within a single connection/transaction: `psql -f` file that ends with the history INSERT, or `-c` with `\i` semantics) insert plain `INSERT` (no ON CONFLICT); add an append-only trigger + revoke on `schema_migration` in 001; record before-fingerprint; take `pg_advisory_lock` for the migration session; set `lock_timeout`/`statement_timeout` and pinned `search_path` in the session preamble.
- **Validation:** New hammers: duplicate-version re-apply must fail; history UPDATE/DELETE must fail; kill-between-migration-and-history scenario impossible by construction.

### F-05 — Delivered candidate schema is a skeletal stand-in for the accepted DB-3 physical design
- **Severity/Timing:** High / C4 (honest labeling) and C5 (real schema). **Category:** design defect + proof defect.
- **Affected:** all `database/migrations/*.sql` vs `db3-fresh-postgres-design-specification-v0-1.md` and the DB-4 package's own migration-mapping table.
- **Observed:** 002 delivers one `scope` table (no governance vocabularies, target anchors, or assignments). 003 delivers one `capture_package` table (no query panels, capture events, validation, provider registry, fingerprints, drift). 004 delivers one `observation` table (no candidate/admission lifecycle, no separate citation identity). 005 has one manifest table (no payload/token structures). 006's audit table has no pairing mechanism to consequential writes. 007 enables RLS on one table, without `FORCE`, `WITH CHECK`, grants, or the three accepted role profiles. 008 is one view (no functions/pagination support). Almost nothing carries the DB-2 concepts (rights, retention, freshness, transitions) the package says it "must preserve."
- **Why it matters:** As harness plumbing proof, thin candidates are defensible. As "Migration Specification" — DB-4's literal name — they are not: any green DB-4 run certifies a toy. The DB-4 mapping table asserts fidelity to DB-3 responsibilities the files do not have, which is documentation-level proof inflation. DB-5 would inherit no real migration set.
- **Correction:** Either (a) relabel the current set explicitly as *harness-proof candidates* and add a DB-4 exit note that the real DB-5 migration set remains unwritten and separately gated, or (b) expand the candidates toward the DB-3 spec before closure. (a) is the honest, bounded option; choose it explicitly rather than by silence.

### F-06 — All hammers run as superuser; RLS/role/privilege claims are untestable as executed
- **Severity/Timing:** High / C4. **Category:** proof defect + security-model defect.
- **Affected:** `postgres_hammers.py::_psql` (`-U POSTGRES_SUPERUSER` everywhere), `007_scope_rls_roles.sql`, `create_bounded_test_roles`.
- **Observed:** Every hammer query executes as `postgres`. Superuser **bypasses RLS entirely**; the table owner also bypasses it because 007 omits `FORCE ROW LEVEL SECURITY`; the policy is `USING`-only (no `WITH CHECK`), so even for constrained roles scoped INSERT/UPDATE leakage is unconstrained. The two test roles are empty `NOLOGIN` shells with **zero grants**; the role hammers assert three catalog rows, never `SET ROLE`, never a denied or permitted statement. The three accepted role profiles (minimal-migration / scope-isolation / typed-read) are unimplemented — the tool ignores profile identity entirely.
- **Counterexample:** Replace the scope policy with `USING (true)`; every role/core hammer still passes.
- **Correction:** 007 adds `FORCE ROW LEVEL SECURITY`, `WITH CHECK`, and profile-specific grants; hammers use `SET ROLE observatory_test_read` (superuser session may SET ROLE to NOLOGIN roles — no passwords needed) and assert both a permitted read and a denied write/cross-scope read.

### F-07 — Hammer-profile JSON manifests are decorative; claimed coverage ≠ executed coverage
- **Severity/Timing:** High / C4. **Category:** implementation defect + documentation defect.
- **Observed:** Nothing in ob-dev reads `database/hammer-profiles/*.json`. Checks are hard-coded Python. `db4_invariants_v1.json` claims H1–H22; the core profile runs 12 checks under partially different IDs. `db4_roles_v1.json` names three role profiles no code loads. `check_database_package.py` "verifies H1–H22 mapping" by reading the JSON that nothing executes — the validator validates the fiction.
- **Why it matters:** Anyone reading the profiles + validator output reasonably concludes 22 hammer families are executed. Twelve structural checks are. This is also the root of the restart pain (see §8): behavior lives in code instead of the repository-owned, SHA-bound data files that already exist for exactly this purpose.
- **Correction:** Make ob-dev load profiles by exact path + SHA, execute the checks the profile declares (from a repository-owned check-manifest), and fail on ID mismatch. This simultaneously fixes coverage honesty and most of the restart cycle.

### F-08 — Authority reference and confirmation digest are self-satisfiable
- **Severity/Timing:** High / C4 (documented honestly) / GOV (hardened). **Category:** security/governance defect.
- **Observed:** `require_authority_reference` validates only string shape (`decisions/*.md`) — the file's existence, acceptance status, and relevance to the operation are unchecked; `decisions/i-made-this-up.md` authorizes a drop. `confirmation_digest` is `sha256(json(op,db,authority))` — computable by the caller from public inputs (and the repo even exposes `digest_payload`). It prevents *accidents* (wrong DB pasted), not unauthorized action. `POSTGRES_AUTHORITY_ENV_VAR` is defined in settings and used by nothing — the runbook's intent (owner binds capability class to a specific decision) is unimplemented.
- **Correction:** Minimum: verify the authority file exists under the observatory root and contains an explicit machine-readable authorization marker for the operation class; bind `OB_DEV_POSTGRES_AUTHORITY` at startup and require the caller-supplied reference to equal it. Document plainly that the digest is an accident-guard, not authorization. Do **not** pretend it is owner approval in proof records.

### F-09 — Disposable-marker enforcement incomplete; marker itself is weak identity
- **Severity/Timing:** High / C4. **Category:** implementation defect.
- **Observed:** `require_disposable_database` checks prefix only. `_verify_marker` is called by drop/reset/roles/migration paths, but **not** by any hammer profile, broken-candidate profile, backup, restore, or semantic-verify path — DB-3: "Name alone is insufficient proof." The marker is a plain superuser-writable table with no binding to database identity (DB-3 required identity binding); any `pg_restore` of a marked dump reproduces the marker in whatever database receives it.
- **Correction:** Call `_verify_marker` in every mutation/proof path; store the database name (and creation authority) inside the marker row and verify it matches `current_database()`.

### F-10 — Broken-fixture detectors match their own fixtures, not the contract; the harness itself never rejects them
- **Severity/Timing:** High / C4. **Category:** test defect + proof defect.
- **Observed:** Detectors key on fixture-specific object names (`broken_observation`, `mutable_evidence`, `unaudited_transition`, `leaked_raw_locator`) and fixture-specific values: `schema_version_divergence` is "detected" by `length(file_sha256) <> 64` — a divergent version 999 with any 64-hex sha is invisible. `unbounded_raw_locator` is detected by a column *named* `absolute_path` — the same column named `note` passes. Structurally, fixtures are executed via direct `psql -f` inside `run_broken_candidate_profile`, **outside** `apply_migration_file`; they never approach metadata validation or history insertion, so the campaign does not prove "the migration harness can reject bad candidates before history insertion." (In fact the fixtures lack the `-- observatory-db4:` metadata line, so `apply_migration_file` path validation would reject them for living outside `database/migrations` — a real but untested rejection.) `sql_failure` fixtures that unexpectedly commit are early-returned without cleanup (residue on the failure path); cleanup is never itself verified.
- **Correction:** Reposition the campaign honestly as *detector self-tests*, and add the missing true harness tests: attempt to apply each fixture through `apply_migration_file` and assert rejection reason + zero history rows; make divergence detection semantic (recompute fingerprint and compare; compare recorded SHA to file SHA) rather than value-shaped; run each fixture in a reset database or verify cleanup with a post-check.

### F-11 — Stale restated authority (recurring regression), two instances
- **Severity/Timing:** Medium / C4. **Category:** documentation defect.
- **Observed:** (a) `decisions/README.md` Last Review Notes: "DB-4 exact artifact inventory and implementation package remain unapproved; implementation remains unauthorized" — contradicted by the acceptance decision indexed in the same file. (b) `POST_V1_DATABASE_ROADMAP.md` DB-4 milestone body still carries package-preparation-era "Forbidden now: ob_dev source implementation / migration execution / real PostgreSQL hammers…" while its Current-state block says these are authorized. This is the third recurrence of the phase-restatement class of drift the post-v1 audit flagged.
- **Correction:** Update both; add an `authority_sync` check that greps milestone-body "Forbidden now" blocks and Last-Review notes against ACTIVE_CONTEXT phase.

### F-12 — Migration execution lacks advisory locking, timeouts, pinned search_path, and before-fingerprints
- **Severity/Timing:** Medium / C5. **Category:** implementation defect.
- **Observed:** No `pg_advisory_lock` around migration application (two concurrent applies of 004 would race history); no `lock_timeout`/`statement_timeout`; no `SET search_path` hardening (fixtures already rely on implicit `public`); before-fingerprint absent; fingerprint = `md5(string_agg(schema.relname))` over tables+views only — **columns, constraints, triggers, policies, functions, and indexes are invisible to drift detection.** Dropping the append-only trigger produces an identical fingerprint.
- **Correction:** Session preamble constants (advisory lock keyed on database, timeouts, `search_path=pg_catalog`); fingerprint from a digest over `pg_dump --schema-only`-class inventory (constraint defs + trigger names + policy defs are already available via the constraint-inventory SQL).

### F-13 — Schema-quality gaps within the delivered candidates
- **Severity/Timing:** Medium / C5. **Category:** design defect.
- **Observed:** Text PKs with no grammar/length CHECKs anywhere (H18 unrepresented physically); `capture_package` has no uniqueness on any natural/idempotency key (H7/H20 unrepresentable at contract level — the concurrency hammer instead probes an ob_dev_control table); RLS on one of five data tables; audit events have no mechanism tying them to consequential writes (H21 structurally unprovable); `observed_value`/`detail` jsonb unbounded; no indexes beyond PK/unique (acceptable for a toy, but contradicts the DB-3 index-family requirements the mapping table claims).
- **Correction:** Fold into the honest-labeling or expansion path chosen under F-05.

### F-14 — Concurrency "race" proof is weak and off-target
- **Severity/Timing:** Medium / C4. **Category:** test defect.
- **Observed:** Two threads each spawn `psql` to `INSERT … ON CONFLICT DO NOTHING RETURNING 1` into `ob_dev_control.concurrency_probe`. It passes even if the two processes run fully serially (no overlap is verified); it tests PostgreSQL PK uniqueness on a control-plane probe table, not "duplicate identity, capture admission, evidence mint" as the accepted spec requires; result parsing is `"1" in {stripped stdout lines}` — brittle. It is *real* PostgreSQL behavior, but a trivially guaranteed invariant.
- **Correction:** Race two inserts of the same `evidence_handle` into `observatory_evidence.observation`; assert exactly one success and one `unique_violation` error class; optionally hold a transaction open in worker A to force actual overlap.

### F-15 — Failure paths discard evidence and can strand residue
- **Severity/Timing:** Medium / C4. **Category:** operational defect.
- **Observed:** `run_profile` early-returns `failed(...)` on first failing check — remaining hammers unexecuted, and the accumulated `items` list is dropped (the failure envelope carries no items), so a reviewer sees only one message. Broken-candidate profile: same early-return pattern; the `sql_failure` unexpected-success path returns without cleanup; cleanup success is asserted only by returncode, never by re-inspection.
- **Correction:** Run all checks, return the full item list with per-item status, mark overall failed; on any failure path, attempt and verify cleanup; record everything (feeds F-01).

### F-16 — Secret-redaction and configuration drift from the accepted runbook
- **Severity/Timing:** Medium / C5. **Category:** security defect (footgun class).
- **Observed:** `sanitize_text` is applied to `error_message` only; `items`/`details` are never scanned; the regex misses connection strings and URI userinfo (`postgres://u:p@host`), both explicitly listed in the runbook's redaction contract. Env names deviate from the accepted key names (`POSTGRES_BIN_DIR` vs `OB_DEV_POSTGRES_BIN_DIR`, `OB_DEV_POSTGRES_CAPABILITY` vs `…_CAPABILITY_CLASS`) — permitted-ish under "fixed constants" language but the prefixless names are collision-prone with other software on the machine. `PGPASSWORD` is injected into a full inherited env copy (fine locally; keep it out of any future logged command line). ob-dev `.gitignore` does not ignore `.postgres-proof/`.
- **Correction:** Centralize redaction over the serialized result envelope; extend patterns (URI userinfo, `PGPASSWORD=`); adopt the `OB_DEV_` prefix; ignore `.postgres-proof/`.

### F-17 — Observatory-side validator and fixture tests are shallow relative to their own spec
- **Severity/Timing:** Medium / C4. **Category:** test defect.
- **Observed:** The accepted metadata contract requires "expected paired SHA-256" per candidate; the metadata format contains **no SHA field** and `check_database_package.py` checks none. `required_prior`/`resulting_version` chains are unchecked; duplicate versions unchecked; fixture files have no metadata validation at all; the symlink-escape obligation is unimplemented; the `prefix-boundary` check is uselessly nested inside the pair loop (appends up to 9 duplicate errors or none). `tests/postgres/*` assert JSON shape only — reasonable as fixture-proof, but they are the *entire* Observatory-side test story.
- **Correction:** Add pair-SHA fields to metadata + validator enforcement; chain validation; duplicate-version detection; fixture-metadata rule ("must NOT carry observatory-db4 forward metadata"); move the prefix check out of the loop.

### F-18 — Cluster-global role residue and cluster-scope mutation under a database-scoped capability
- **Severity/Timing:** Medium / C4. **Category:** governance + operational defect.
- **Observed:** `create_bounded_test_roles` creates **cluster-wide** roles under `postgres_disposable_only`, i.e., a "disposable database" capability performs mutation that outlives any database drop. The prompt states cleanup may not have run; nothing in the repo records either creation or cleanup. `drop_bounded_test_roles` (itself an unaccepted tool, F-02) at least verifies removal.
- **Correction:** Verify current `pg_roles` state, run/record cleanup, and note in the DB-4 closure package that role lifecycle is cluster-scope and must always pair create/drop within one campaign.

### F-24 — Public ngrok exposure of an unauthenticated mutation-capable MCP server
- **Severity/Timing:** High / C4 (operational posture; fix independent of code). **Category:** security defect.
- **Observed:** `ob-dev/README.md` documents exposing `http://127.0.0.1:8781/mcp` through `ngrok http --domain=ob-dev.ngrok.dev`, explicitly "no-API-key," so ChatGPT Desktop can connect. That URL, if discovered or guessed (it is a stable reserved subdomain), grants any internet caller: file write/delete across `C:\dev\ob-dev` and `C:\dev\observatory`, Git staging/commits, subprocess-running test profiles (which execute repo code), and — whenever the owner has elevated `OB_DEV_POSTGRES_CAPABILITY` and set `POSTGRES_PASSWORD` — superuser-driven PostgreSQL mutation, bounded only by the disposable-prefix logic. The digest/authority checks are self-satisfiable (F-08), so they do not mitigate an external caller.
- **Correction:** Put an authentication layer in front (ngrok OAuth/basic-auth/IP allowlist, or FastMCP bearer auth), keep the tunnel up only during active sessions, and keep `POSTGRES_PASSWORD`/elevated capability unset except during owner-supervised proof windows. Record this as an operational invariant in the runbook.

### Low / Advisory
- **F-19 (Low):** `postgres_verify_semantic_restore` is annotated READ_ONLY yet gated on `restore_proof_authorized` — annotation/capability inconsistency. `migration_status`/`migration_history_read` require the disposable prefix, which will need widening at DB-5. Dead `POSTGRES_AUTHORITY_ENV_VAR` (also F-08).
- **F-20 (Low):** `H20-concurrency` structural check asserts *exactly 2* unique indexes on `observation` — the same exact-count fragility class already bitten by the ACL detector; any added index flips it to false-failure.
- **F-21 (Low):** `verify_semantic_restore` counts schemas only — "semantic" restore verification is currently a namespace count; row-level continuity (migration history rows, marker, verification rows) is not compared. Fine for DB-4 if honestly labeled; insufficient for DB-8.
- **F-22 (Advisory):** `database_class()` classifies any unknown name as `production` — fail-closed in effect but semantically misleading in evidence output; prefer an `unknown_unauthorized` class.
- **F-23 (Advisory):** Broken-fixture execution order is dict-insertion order; make it explicit/sorted for reproducible proof records. `009_excess_role_privilege` cleanup revokes only on the probe table — acceptable only because the substrate is disposable.
- **F-25 (Advisory):** Rollback `001` (`DROP SCHEMA observatory_meta CASCADE`) destroys migration history itself — correct for full teardown, but a partial rollback to version ≥001 that later re-runs forward migrations depends on F-04's mutable-history bug to "work." After F-04's fix, re-application semantics need an explicit rule (history rows for rolled-back versions: delete via authorized rollback path, or append a rollback event).

---

## 4. Milestone-by-milestone assessment

### DB-1
Governance/policy milestone. The three accepted artifacts (hammer matrix v0.2, gate policy v0.2, result-register v0.1) are genuinely high quality: proof classes are ordered by substrate and explicitly non-substitutable; "a successful tool call is not automatically a hammer pass," "a tool catalog is not execution evidence," and "pass without a proof class and execution surface is invalid" are all present. The register contract even pre-forbids exactly the inflation this audit found in DB-4 code. **Trustworthy as policy.** Condition: the policy is not yet self-enforcing (no validator implements the register; F-01), and DB-1's own housekeeping shows the stale-restatement regression is unresolved (F-11).

### DB-2
Freeze v0.2.1 is SHA-bound (`7c24d38e…`), immutable, singular normative input, cleanly separated from retired lineage. Indexing in `planning-inbox/README.md` correctly labels every historical/invalidated sibling. **Trustworthy as a contract.** Condition: fidelity to it is not carried into DB-4 physical candidates (F-05); this is a downstream defect, not a DB-2 defect.

### DB-3
The design spec is the phase's strongest artifact — forced RLS, marker+identity binding, role least-privilege with NOLOGIN groups, append-only history, backup-before-migration, before/after fingerprints, advisory-lock/serialization concurrency, "name alone is insufficient," "tool existence never creates authority." **Trustworthy as specification.** Condition: DB-4 implements a small fraction of it (F-04/05/06/09/12); the spec currently over-describes the enforcement that exists.

### DB-4 (active)
Not closable. Against `acceptance-gate-policy-v0-2.md` §DB-4's five closure conditions:
1. "accepted ob-dev tools implemented and owner-refreshed" — **partial/violated**: 30 tools vs accepted 28 (F-02).
2. "disposable class protected and operational" — **partial**: marker exists but is unenforced on proof paths and weakly bound (F-09).
3. "exact-path/SHA forward+rollback works" — **partial**: works, but history is mutable/non-atomic (F-04) and metadata lacks the required pair SHA (F-17).
4. "mandatory hammers shown failing against broken candidates" — **not met**: detectors match fixture names/values and never traverse the real harness (F-10).
5. "required passing hammers earn real_postgres_disposable_pass; result-register entries complete and reviewable" — **not met**: no records exist (F-01) and passing checks are structural, not hostile (F-03).
Plus the explicit rule "Fixture/mock/in-memory/owner-local results cannot satisfy DB-4 gates" — and right now everything reviewable *is* fixture/JSON-shape proof.

### DB-5 readiness
Blocked. Requires an accepted migration set proven at `real_local_database_pass`. The candidate set is a harness stand-in (F-05); migration/history integrity is unsound (F-04/F-12); role and RLS enforcement are unimplemented (F-06). DB-5 must remain inactive.

---

## 5. Hammer-by-hammer assessment (DB-4 core profile as implemented)

| ID (as coded) | Matrix intent | Current proof | Actual strength | Counterexample | Status | Replacement |
|---|---|---|---|---|---|---|
| H1 | Scope isolation | count of 7 observatory_ namespaces | catalog presence | rename a schema → false-fail; wrong scope data invisible | weak | SET ROLE + cross-scope read denied under FORCE RLS |
| H2 | Rights fail-closed | scope table exists | mislabeled structure | no rights concept in schema at all | false-labeled | attempt use without rights row → blocked |
| H3 | Retention enforcement | 1 FK in capture schema | mislabeled structure | drop retention has no representation | false-labeled | purge-transition + read-after-purge blocked |
| H5 | No strategy storage | 1 UNIQUE in evidence | mislabeled structure | a strategy table would still pass | false-labeled | forbidden-schema register check + insert rejection |
| H6 | CapturePackage validation | 2 CHECKs on support_manifest | partial structure | H6 is capture-envelope, not raw manifest | mis-mapped | required-field/immutability assertion on capture_package |
| H9 (not DB-4 core) | Freshness/claims | append-only trigger present (by name) | catalog presence | trigger body could be a no-op | weak | fire UPDATE/DELETE → expect exception |
| H12 | Raw manifest integrity | RLS flag on observation | mis-mapped (H12≠RLS) | policy USING(true) passes | false-labeled | hash/pointer invariant + locator-exposure rejection |
| H15 | Evidence ID/citation | policy row exists | catalog presence | USING(true) passes | weak | duplicate evidence_handle → unique violation |
| H18 | Hostile input | read-view exists | unrelated | no identifier grammar in schema | absent | oversized/bad-grammar identifier rejection |
| H19 | Append-only obs | schema_migration table exists | unrelated catalog | table exists but is mutable | false-labeled | UPDATE audit.event → expect rejection |
| H21 | Audit-first | restore_verification table exists | unrelated catalog | no audit pairing exists | false-labeled | consequential write without audit row → blocked |
| H22 | Migration recovery | count of 7 tables | catalog presence | fingerprint blind to trigger loss | weak | forward+rollback+failure with real fingerprint diff |
| H4 | Customer-private reject | — | absent | — | missing | private-field insert rejection |
| H7/H8/H10/H11/H13/H14/H16/H17 | various | — | absent from executed core | — | missing | out of DB-4 core scope, but claimed by profile JSON |

Migration profile (`H22-forward/rollback/failure-recovery`): forward = table count; rollback/failure = temp-table-in-aborted-transaction — both prove generic PostgreSQL transaction atomicity, not the project's migration harness. Role profile: three catalog-row asserts, no SET ROLE. Concurrency: see F-14. Restore: three catalog counts, no continuity comparison.

**Overall hammer verdict:** of 12 executed core checks, ~9 are structure catalogs mislabeled with hostile-claim IDs, 0 exercise a forbidden operation and observe rejection, and 100% are marked `real_postgres_disposable_pass`. This is the single most important DB-4 defect class.

---

## 6. Migration-by-migration assessment

| File | Purpose | Deps | Constraints created | Rollback | History behavior | Risks | Required correction |
|---|---|---|---|---|---|---|---|
| 001 identity_namespaces | meta schema + schema_migration(version PK, sha, fingerprint) | none | PK on version | DROP SCHEMA meta CASCADE | history table itself created here; **no append-only protection** | history mutable/rewritable (F-04); no before-fingerprint | add append-only trigger + revoke on schema_migration; plain INSERT semantics |
| 002 governance_scope | scope(scope_class CHECK) | 001 | PK, CHECK(2 values) | DROP SCHEMA core CASCADE | n/a | delivers 1 of many DB-2 governance concepts (F-05) | expand or relabel |
| 003 capture_provider | capture_package + FK→scope | 002 | PK, FK, NOT NULLs | pair present | n/a | no idempotency uniqueness (F-13); no capture-event/provider registry | add natural-key unique; expand |
| 004 evidence_identity | observation + FK→package + UNIQUE(handle) | 003 | PK, FK, UNIQUE, jsonb NOT NULL | pair present | n/a | no candidate/admission lifecycle; unbounded jsonb | expand per DB-2 spine |
| 005 raw_support | support_manifest + FK + retention CHECK + locator_exposed CHECK(=false) | 004 | PK, FK, 2 CHECKs | pair present | n/a | locator boundary present but thin; no payload/token separation | expand |
| 006 audit_append_only | audit.event + reject_mutation() trigger (BEFORE UPDATE/DELETE) | 005 | PK; append-only trigger | DROP SCHEMA audit CASCADE | n/a | trigger never fired by any hammer (F-03); no audit-first pairing (F-13) | add behavioral hammer; add pairing mechanism |
| 007 scope_rls_roles | ENABLE RLS + USING policy on observation | 006 | RLS policy (USING only) | DROP POLICY + DISABLE RLS | n/a | no FORCE, no WITH CHECK, no grants, owner+superuser bypass (F-06) | add FORCE/WITH CHECK/grants; SET ROLE hammers |
| 008 typed_read | observation_summary view | 007 | view | DROP SCHEMA read CASCADE | n/a | no pagination/functions; view exposes observed_value directly | expand for DB-7 |
| 010 recovery_verification | restore_verification(migration_count CHECK≥0) | 008 | PK, CHECK | DROP TABLE | resulting_version 010 from prior 008 | 009 gap intentional & documented (OK) | — |

Cross-cutting migration architecture corrections (all F-04/F-12): single-connection migration+history atomicity; advisory lock; lock/statement timeouts; pinned search_path; before+after fingerprint over a constraint/trigger/policy-inclusive inventory; append-only history enforcement in-DB; plain INSERT (no ON CONFLICT). The runner-owns-history vs migration-owns-history question: prefer the **migration file owns its history INSERT as its last statement inside the same transaction**, with the runner supplying only the validated SHA as a bound parameter — this removes the split-brain window entirely.

---

## 7. Broken-fixture assessment

| Fixture | Intended violation | Actually invalid under contract? | PG-reject or hammer-detect? | Detector precise? | Name-dependent? | Passes if empty/no-rows? | Count=1 unsafe? | Cleanup after pass+fail? | Own DB? | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| dirty_constraint_seed | CHECK added over violating row | yes | PG rejects (ADD CONSTRAINT fails) | n/a (returncode) | no | no | no | pass:n/a fail:no-cleanup path | shared | genuine PG-reject; OK but shares DB |
| partial_migration_failure | 1/0 mid-transaction | yes | PG rejects (aborts) | n/a | no | no | no | fail path returns w/o cleanup | shared | genuine; residue risk on unexpected-commit path |
| excess_role_privilege | GRANT ALL … TO PUBLIC | yes | hammer-detect via aclexplode grantee=0, count>0 | improved (threshold, live tree) | keys on probe table name | needs setup table | fixed (F-live) | cleanup revokes+drops | shared | improved but detects seeded probe, not the fixture's own PUBLIC grant |
| missing_audit_pair | table w/o audit trigger | weakly | hammer-detect NOT EXISTS trigger | name-keyed | yes | passes if table absent | no | cleanup drops | shared | detector matches `unaudited_transition` by name |
| missing_scope_boundary | obs table w/o scope FK | weakly | hammer-detect NOT EXISTS FK | name-keyed | yes | passes if absent | no | cleanup drops | shared | matches `broken_observation` by name |
| mutable_evidence | evidence w/o append-only | weakly | hammer-detect NOT EXISTS trigger | name-keyed | yes | passes if absent | no | cleanup drops | shared | matches `mutable_evidence` by name |
| schema_version_divergence | bogus history row | yes | hammer-detect length(sha)<>64 | **imprecise** | value-keyed | needs history table | no | cleanup deletes | shared | 64-hex bogus sha is invisible; SHA/file mismatch never checked |
| unbounded_raw_locator | locator column stored | yes | hammer-detect column named absolute_path | **imprecise** | column-name-keyed | passes if column renamed | no | cleanup drops | shared | rename to `note` defeats it |

**Structural finding (all fixtures):** they never pass through `apply_migration_file`, so the campaign does **not** prove the migration harness rejects bad candidates before history insertion — it proves a bespoke detector recognizes eight specific hand-built schemas. Fixtures also lack `-- observatory-db4:` metadata, so the real harness would reject them at path/metadata validation (untested).

**Missing fixtures to add** (highest value): history rewrite via re-apply (proves F-04); duplicate migration version with different SHA; migration applied without history / history without schema; RLS bypass through table owner (no FORCE); role membership escalation; SECURITY DEFINER function; trigger disablement (`ALTER TABLE … DISABLE TRIGGER`); constraint `NOT VALID` left unvalidated; cross-scope FK; invalid UTC / naive timestamp; concurrent migration execution (advisory-lock absence); search_path hijack (attacker object shadowing an unqualified reference).

---

## 8. ob-dev architecture assessment

**Safety:** The fixed-root, no-shell, no-arbitrary-SQL, SHA-locked-edit, exact-manifest-commit model is sound and well-tested for the file/Git surface. The PostgreSQL surface is weaker than its own contract: superuser-for-everything (F-06), self-satisfiable authority/digest (F-08), marker not enforced on proof paths (F-09), redaction partial (F-16). Most acutely, the ngrok exposure (F-24) turns every one of these local footguns into a remotely reachable one.

**Maintainability:** Good module separation (contract/runtime/inspection/control/hammers/backup). The critical anti-pattern is **behavior encoded in Python while a parallel, SHA-bound, repository-owned profile/data-file system sits unused** (F-07). This is both a correctness problem (claimed≠executed coverage) and the direct cause of the restart pain.

**Test quality:** ob-dev tests are mostly contract/shape and monkeypatched-subprocess; `test_postgres_hammers.py` monkeypatches `_psql` to fixed strings — it verifies control flow, never real PostgreSQL. That is legitimate fixture-proof, but `test_server.py`'s expected-tool set was edited to match the over-count (F-02), which converts a contract guard into an implementation mirror — the most dangerous test-quality regression here.

**Restart ergonomics (the owner's stated pain).** Every code correction requires: stop server → edit → restart `start.ps1` → refresh/rescan the ChatGPT connector's tool actions. Because tool *behavior* lives in code, every behavioral fix is a code change is a restart. Safe ways to minimize, in priority order:
1. **Data-driven hammer/profile execution (biggest win, also fixes F-07).** Load the already-existing profile JSONs by exact path+SHA and execute a repository-owned check manifest. Then iterating on hammers/fixtures/checks is editing SHA-bound *data files* (already a bounded ob-dev capability) — no code change, no restart. The tool surface freezes; behavior becomes versioned data.
2. **Front controller + reloadable workers.** Keep the FastMCP tool registrations (names/schemas/annotations) frozen in a thin stable module; dispatch to an implementation module reloaded via `importlib.reload` behind an owner-invoked `reload_implementation` action (read-only annotation, no new authority, no shell). The connector never sees a surface change, so no rescan.
3. **Owner-controlled local restart script** that stops the process, runs the full validation profile, and only restarts on green (test-before-restart batching) — reduces failed-restart churn.
4. **Batch staging:** make all planned code edits, validate once, restart once. Cultural, but cheap.
Explicitly avoid: self-modifying tools, self-`exec`, shell access, or loosening fixed roots. Option 1 is recommended first because it also resolves F-07 and shrinks the change surface that needs restarts at all.

**Recommended architecture:** freeze the 28 (or owner-accepted 30) tool surface; move all hammer/fixture/check definitions into SHA-bound repository data consumed at call time; emit result-register records from the tool layer; add real SET ROLE execution and authority binding; put auth in front of the network exposure.

---

## 9. Missing tests (prioritized backlog)

**P0 (DB-4 closure):**
1. Register-emission + register-validator tests (F-01).
2. Behavioral hammer tests with expected failures: audit UPDATE rejected; duplicate evidence_handle rejected; cross-scope read denied under SET ROLE + FORCE RLS; history rewrite rejected (F-03/F-04/F-06).
3. `apply_migration_file` rejects each broken fixture with a specific reason + zero history rows (F-10).
4. Migration+history atomicity: simulated failure after DDL leaves no history; after fix, impossible by construction (F-04).
5. Tool-surface contract test derived from a committed accepted-registry doc, not an inline set (F-02).

**P1 (DB-5 precondition):**
6. Advisory-lock/concurrent-migration test; lock/statement-timeout presence (F-12).
7. Fingerprint sensitivity test: dropping a trigger/policy changes the fingerprint (F-12).
8. Metadata pair-SHA + version-chain + duplicate-version validator tests (F-17).
9. Marker identity-binding + marker-required-on-proof-paths tests (F-09).

**P2:** redaction over full envelope incl. URI userinfo/connection strings (F-16); semantic-restore row-continuity test (F-21); role-residue create/verify/drop lifecycle test (F-18).

---

## 10. Recommended remediation batches

**Batch A — DB-4 closure blockers.** Goal: make closure honest. Files: `postgres_hammers.py`, `postgres_control.py`, `007_*.sql`, `006_*.sql`, `001_*.sql`, new register emitter, `hammers/results/`, `server.py`+`test_server.py` (registry), `decisions/*` (tool acceptance), `decisions/README.md`+`POST_V1_DATABASE_ROADMAP.md` (stale authority), README (tool count), operational auth for ngrok. Grouped because none can be split without leaving a false-green gate. Tests: §9 P0. Stop conditions: any hammer passes while its enforcement mechanism is deliberately broken; any registry mismatch; any secret in a result. Authority: owner ruling on the two extra tools; **does not change doctrine** (it enforces existing doctrine). Note F-05 labeling decision required here.

**Batch B — migration/history integrity.** Files: `postgres_control.py`, `001_*.sql`, metadata format + `check_database_package.py`, `tests/test_database_package.py`. Single-connection atomic migration+history; append-only history; advisory lock; timeouts; search_path; real fingerprint; pair-SHA. Tests: §9 P1 6–8. Authority: within DB-4 package intent (transaction rules already accepted). Doctrine: unchanged.

**Batch C — hammer realism.** Files: `postgres_hammers.py`, profile JSONs, fixtures, new detectors, data-driven check manifest. Re-key to matrix IDs; behavioral expected-failures; semantic divergence/locator detection; fixtures through the real harness; missing fixtures (§7). Tests: §9 P0 2–3, P1 9. Authority: DB-4 package intent. Doctrine: unchanged.

**Batch D — ob-dev ergonomics & restart reduction.** Files: hammers→data-driven loader, thin front controller + reloadable worker or owner restart script, `.gitignore`, README. Grouped: all reduce restart churn and freeze the surface. Tests: profile-load + SHA-mismatch rejection. Authority: none beyond existing bounded-edit; **must not** add shell/self-modify. Doctrine: unchanged.

**Batch E — DB-5 preconditions.** Files: expanded migration candidates toward DB-3 spec (or the explicit "harness-only, real set deferred" ruling), role profiles, RLS FORCE/WITH CHECK/grants, DB-5 authorization decision draft. Tests: full role/RLS/scope hammers at intended proof class. Authority: **new owner DB-5 decision required**; do not begin without it. Doctrine: unchanged but this is the boundary where governed-database law becomes live.

---

## 11. Closure recommendation

**DB-4 may close after listed implementation and proof corrections.**

Specifically Batches A, B, and C must land, with real result-register records at `real_postgres_disposable_pass` for the mandatory hammer families (each proven by a hammer that fails when its mechanism is broken), the tool-registry deviation ruled, the two stale-authority documents corrected, and the network-exposure operational control in place. Documentary-only closure is not available: the defects are in executed behavior and in the absence of durable proof, not merely in prose.

## 12. DB-5 recommendation

**DB-5 must remain inactive.**

DB-5 may become eligible only after DB-4 closes honestly *and* Batch E resolves the migration-set fidelity question (F-05) with either an accepted expansion or an explicit ruling that DB-5 will author its own real migration set from the DB-3 spec. A new owner decision naming governed database creation, exact role profiles, and exact migration paths+SHAs remains mandatory and is not implied by any DB-4 result.

---

## 13. Verified praise (evidence-tied)

- The recovery-and-retirement governance arc is real and clean: reflog + `planning-inbox/README.md` labeling would stop a future agent from resurrecting the five retired artifacts (verified against both).
- `per-hammer-result-register-v0-1.md` and `acceptance-gate-policy-v0-2.md` pre-forbid the exact inflation this audit found in code ("a successful command is not automatically a hammer pass"; proof classes non-substitutable). The policy is ahead of the implementation — the gap is enforcement, not intent.
- The ob-dev file/Git surface (fixed roots, SHA-locked edits, exact-manifest commits, no-shell, closed schemas, integrity scan) is well-built and well-tested; the recent `replace_exact_text` no-op fix is correct and thoroughly tested.
- Marker+prefix disposable-name discipline, protected-name rejection, and the `CREATE DATABASE observatory` / governed-name guards are genuinely present in code and tests — the *governed database was not created*, matching the stated boundary.

## 14. Final standard note

The happy path passed, and that is precisely the risk: nearly every executed DB-4 "hammer" confirms that a correctly-built object *exists*, never that a hostile action is *refused*. Combined with zero durable proof records and a tool count that drifted past its own hard gate, the DB-4 proof is presently paperwork the project's own gate policy would reject. Fix the three closure batches, make hammers fail when the schema is sabotaged, and write the register — then DB-4 will deserve to close.

*This report is advisory. It authorizes nothing: no closure, no DB-5, no database/role/migration/provider work. Read-only inspection only was performed.*
