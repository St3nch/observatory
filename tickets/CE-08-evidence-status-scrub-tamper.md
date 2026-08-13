# CE-08 — Evidence status, report-only scrub, and refuse verification

**Status:** done
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-07 — Read API: health and attempt envelope
**Approved by:** Project Steward
**Start commit:** b5d43bb5ffc14e563fccb51fe8f801d1ec8e3a0e

## What to build

End-to-end behaviour this ticket makes work: `python -m observatory.evidence status` and
report-only `scrub`; status recognizes a valid openable format-2 store and fails closed
when FORMAT validation prevents open; scrub
examines commitment-claiming event directories, runs normative verification, and reports
candidate paths that fail—without mutating the store; and planted integrity failures
confirm that **existing** CE-06 derive refuse and CE-07 API 409 behaviors still hold.

This ticket **does not** introduce derive refuse or API 409 for the first time; those are
CE-06 and CE-07. It **does not** freeze public scrub diagnostic class names, codes, report
schema, media type, output ordering, or wording taxonomy.

## Authority

- `docs/specs/capture-event-v2.md` — §Rebuildable PostgreSQL / entrypoints / API (`status` and `scrub` CLIs; 409 `evidence_integrity_failure` on failed verify-on-read)
- `docs/specs/capture-event-v2.md` — §FORMAT.json (fail-closed open)
- `docs/specs/capture-event-v2.md` — §Canonicalization and verify-on-read (steps 1–6; fail closed; never silent repair)
- `docs/specs/capture-event-v2.md` — §Commit visibility (Evidence only after verified manifest + bodies + COMMITTED)
- `docs/specs/capture-event-v2.md` — Capture.request deep-equals Attempt.request (aggregate verification)
- `VISION.md` — §What v1 must prove item 6 (basic tamper detection; report-only scrub refuse damaged material as valid Evidence)
- `decisions/decisions.md` — D8 verify-on-read; Evidence Store scrub in cost/consequence language without authorizing destructive repair

## Scope

- `evidence status`: successfully recognizes an openable format-2 store and fails closed on FORMAT validation failure
- Report-only `scrub`:
  - examines event directories that **claim commitment** (bear a `COMMITTED` marker);
  - performs the normative verification required by committed authority (verify-on-read family);
  - processes clean verified candidates without falsely reporting them as verification failures and leaves them admissible as Evidence;
  - **reports the candidate path** when that verification fails;
  - does not mutate clean or damaged candidates, repair, delete, quarantine, or silently accept a failed candidate;
  - failed candidates are not used as valid Evidence
- Fault-injection tests for the normative verification **families** below (test cases, not public product labels)
- End-to-end exercises of CE-06 derive refuse and CE-07 API 409 against planted failures

## Out of scope

- Freezing scrub diagnostic class names, codes, report schema, media type, ordering, or wording
- Required scrub-report categories for: directories lacking `COMMITTED`; duplicate-Capture inventory; unreferenced-object inventory; repair/delete/quarantine suggestions; open-ended extras
- Claiming to implement derive refuse or API 409 for the first time
- Off-host backup (F6); multi-process hammers (F4/F7)

## Required verification test families (not public taxonomy)

Automated fault injection must cover these normative verification failures for commitment-claiming candidates:

1. **COMMITTED / directory / manifest identity / re-JCS verification failure**
   (Spec §Verify-on-read steps 2–3; D8 #5; COMMITTED identity)
2. **Cited body digest or byte-size verification failure**
   (Spec §Verify-on-read step 5)
3. **Capture-to-Attempt aggregate verification failure**
   including request testimony that does not deep-equal the verified Attempt request, or a referenced Attempt that cannot be verified
   (Spec Capture aggregate / cross-field rules; verify-on-read step 4)

Directories lacking `COMMITTED` remain non-Evidence and must not be admitted; they are
**not** a required scrub-report category. The ≤1 Capture invariant remains enforced by
CE-04; multi-Capture inventory is **not** a CE-08 reporting taxonomy.

## Acceptance criteria

- [x] `python -m observatory.evidence status` successfully recognizes a valid, openable format-2 Evidence Store.
- [x] `python -m observatory.evidence status` fails closed when FORMAT validation prevents opening the store.
- [x] `python -m observatory.evidence scrub` processes clean, commitment-claiming Attempt and Capture candidates without falsely reporting verification failures; clean verified candidates remain admissible as Evidence.
- [x] `python -m observatory.evidence scrub` is report-only: for each commitment-claiming candidate that fails normative verification, it reports the candidate path and does not mutate, repair, delete, quarantine, or accept it as valid Evidence.
- [x] Scrub does not mutate either clean or damaged candidates.
- [x] Fault injection for each of the three verification families above causes scrub to report the candidate path and causes the candidate not to be used as valid Evidence.
- [x] Uncommitted directories (no `COMMITTED`) are not admitted as Evidence.
- [x] Against the same planted failures, derive refuses only rows that depend on damaged Evidence: a damaged Attempt yields no Outcomes or Observations from that Attempt, while damage limited to a Capture or cited body yields no Capture-stage Outcome or Observations from that Capture and does not suppress the independently verified parent Attempt's Attempt-stage Outcome; API still returns HTTP 409 with a body containing `evidence_integrity_failure` when a read would surface damaged cited Evidence (CE-07 behavior).

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy` as applicable
- Substrate: real Evidence FS; **real PostgreSQL** and API where refuse integration is exercised
- Forbidden claims: scrub is not repair; not off-host recovery; not a public diagnostic taxonomy freeze

## Required automated tests

- status recognizes a valid, openable format-2 store
- status FORMAT fail-closed
- scrub accepts clean committed Attempt and Capture candidates without false failure reports and leaves them admissible
- scrub report-only non-mutation
- Fault injection: identity/COMMITTED/re-JCS family
- Fault injection: body digest/size family
- Fault injection: Capture–Attempt aggregate family
- Uncommitted dirs not admitted as Evidence
- Integration: derive refuses damaged-dependent rows while preserving the independently verified parent Attempt-stage Outcome when damage is limited to a Capture or cited body
- Integration: API 409 + `evidence_integrity_failure` on damaged cited Evidence

## Forbidden claims

- Public scrub class names/codes/schema as product contract
- First introduction of derive refuse or API 409 (those are CE-06 / CE-07)
- Repair, delete, quarantine, orphan inventory, multi-Capture inventory as required reports

## One implementation commit must prove

Status + report-only scrub + end-to-end refuse verification against planted failures—without needing further tickets for that claim.

## Later tickets

Later tickets are **not** required to make this ticket’s acceptance criteria truthful.

## Beyond authority

This ticket adds **no** behavior beyond committed authority.

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

- End commit: supplied in the implementer handoff report (a commit cannot
  embed its own final hash).
- Acceptance evidence:
  - `uv run pytest -q` — 468 passed
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Status: `test_status_recognizes_openable_format2_store`,
    `test_status_fails_closed_on_missing_format`,
    `test_status_fails_closed_on_wrong_format_without_tmp_purge`
  - Read-only inspect: `test_inspect_store_does_not_purge_tmp`,
    `test_scrub_format_failure_does_not_purge_tmp`
  - Clean scrub: `test_scrub_accepts_clean_committed_attempt_and_capture`,
    `test_scrub_cli_module_entrypoint_clean`
  - Identity family:
    `test_scrub_reports_wrong_committed_contents`,
    `test_scrub_reports_manifest_digest_mismatch`,
    `test_scrub_reports_incorrect_terminal_identity`,
    `test_scrub_reports_valid_capture_at_wrong_shard`,
    `test_scrub_reports_valid_attempt_at_wrong_branch`,
    `test_correctly_located_bundles_remain_accepted`,
    `test_scrub_reports_noncanonical_jcs_with_matching_identity`,
    `test_scrub_reports_self_consistent_schema_failure`
  - Body family:
    `test_scrub_reports_request_body_tamper`,
    `test_scrub_reports_response_body_tamper`,
    `test_scrub_reports_pool_object_tamper`
  - Aggregate family:
    `test_scrub_reports_capture_request_mismatch`,
    `test_scrub_reports_uncommitted_parent_attempt`
  - Uncommitted: `test_uncommitted_directory_is_not_admitted_or_reported`
  - Failed not valid: `test_failed_candidates_are_not_valid_evidence`
  - Derive + API:
    `test_derive_and_api_against_damaged_attempt`,
    `test_derive_and_api_against_damaged_capture`,
    `test_derive_and_api_against_damaged_response_body`
- Unproven limits:
  - Status uses ordinary `open_store` and may purge `.tmp/` on a
    valid root. Scrub never does.
  - Paths are POSIX-relative to the Evidence root.
  - No orphan-object, duplicate-Capture, or uncommitted inventories.
  - Not off-host, crash, or concurrent-writer proof.
  - Report lines are candidate paths only; not a frozen schema.
- Review findings remaining:
  - Scrub exit 1 means one or more failed candidates; 2 is FORMAT.
  - Steward decision: `status` remains an ordinary openability check and
    therefore uses `open_store`, including D7 post-FORMAT `.tmp/` purge on
    a valid root. Report-only `scrub` uses non-mutating `inspect_store`.
  - Formal review found and remediation closed a full-path verification gap:
    a self-consistent valid bundle at a wrong shard or Attempt branch is now
    rejected by the shared authoritative verifier, not only by scrub.
  - True noncanonical JSON with matching stored-byte identity, marker, terminal
    name, and normative path is independently rejected by re-JCS verification.

## Closure

<!-- Project Steward only -->

- Closed at commit: `53cf44f00aa0d93afc79392fedc4089eb730ef4a`
- Evidence accepted: yes
- Steward verification:
  - Exact comparison: `b5d43bb5ffc14e563fccb51fe8f801d1ec8e3a0e`
    through `53cf44f00aa0d93afc79392fedc4089eb730ef4a`
  - `uv run pytest -q` — 468 passed on real PostgreSQL 18
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Status fail-closed, exact marker-parent discovery, report-only
    nonmutation, all verification families, normative full-path enforcement,
    dependency-bounded derive refusal, and API integrity 409 accepted
