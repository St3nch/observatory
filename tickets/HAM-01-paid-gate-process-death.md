# HAM-01 — Paid-gate process-death Evidence hammer

**Status:** review
**Authority:** D6, D8, D9; deferred trigger F4
**Kind:** bounded Evidence Store hammer
**Blocked by:** none (PF-02 is done)
**Approved by:** Project Steward
**Start commit:** `c67efc6271db6e9a986e188d56e2b3cffb2896dd`

## Why this ticket exists

F4 requires one dedicated hammer before any real paid capture is authorized. PF-02 proved
the DataForSEO sandbox transport deterministically and with one real no-spend smoke, but
ordinary tests do not prove what the Evidence tree says after abrupt process death around
the Attempt-before-send and Capture-after-response boundaries.

This ticket supplies that narrow proof. It spends no DataForSEO credit and adds no paid
host. Passing it satisfies the F4 prerequisite for the next separately ticketed,
small-budget DataForSEO probe runner; it does not itself authorize that runner or any paid
call.

## Exact claim to prove

On one supported local POSIX Evidence Store with one capture process and one loopback
server:

1. The server cannot observe a request until the corresponding Attempt and request body
   are committed, durably ordered by the existing store protocol, and independently
   verify on read.
2. Abrupt child-process death at each exercised Evidence mutation/durability milestone
   before send leaves zero requests and either no committed Attempt or one fully verified
   committed Attempt. It never leaves malformed material that claims commitment.
3. Once the server observes a request, it observes exactly one. The Attempt already
   verifies at that instant.
4. Abrupt child-process death after the response and during Capture commit leaves the
   verified Attempt plus either no committed Capture or one fully verified Capture. The
   former is honest authorized/unresolved history; it is never labeled definitely unsent
   and is never retried automatically.
5. A no-fault control performs exactly one exchange and leaves exactly one verified
   Attempt, one verified Capture, and a clean scrub.
6. Sentinel credentials do not appear in Evidence bytes, child stdout/stderr, exception
   text, or the loopback testimony.

This is process-death and ordering proof. It is not sudden-power-loss, storage-device
cache, off-host recovery, concurrent-writer, or production-provider proof.

## Required hammer design

Add one focused, opt-in test module:

`tests/test_paid_gate_process_death_hammer.py`

The ordinary suite must collect it but skip its destructive/process-kill matrix unless
`OBSERVATORY_RUN_PAID_GATE_HAMMER=1`. The opt-in run uses pytest's `--basetemp` under
an operator-selected, empty path on the actual supported local POSIX filesystem.

The hammer must:

- use real filesystem operations from the exact concrete `EvidenceStore`;
- use the accepted PF-02 post-gate transport path with sentinel credentials and only a
  real `127.0.0.1` loopback HTTP server;
- perform no DataForSEO, provider, DNS, or other public-network call;
- spawn a child process for each fault case and terminate that child with
  `os._exit(97)` after the selected real operation has completed, so Python exception
  unwinding or cleanup cannot make the result look safer;
- discover or record the exercised commit milestones from the actual implementation
  rather than asserting only a hand-written fantasy sequence;
- cover, at minimum, terminal bundle-directory creation, manifest installation,
  bundle-body installation, `COMMITTED` installation, and the directory-fsync boundary
  for both Attempt and Capture where that operation exists;
- prove that the matrix actually reached both pre-send Attempt work and post-response
  Capture work; an empty, skipped, or Attempt-only matrix is failure;
- give every child a fresh Evidence root so one fault case cannot contaminate another;
- bound child/server waits and fail on timeout instead of hanging;
- preserve child exit status and only fixed non-secret diagnostics.

At the moment the loopback server receives a request, the parent/server side must use
non-mutating `inspect_store` and verify the sole corresponding Attempt independently.
Do not accept a child-held object or an in-memory success flag as this proof.

## Postmortem rules for every fault case

Before any cleanup-capable open:

1. inspect the raw tree without mutation;
2. enumerate commitment-claiming Attempt/Capture directories;
3. independently verify every committed candidate;
4. run report-only scrub;
5. scan all regular Evidence files and captured terminal surfaces for every sentinel
   login/password/Basic-token form.

Then an ordinary `open_store` may purge `.tmp/` residue. Compare before/after paths and
prove that cleanup removed only permitted temporary residue; it must not change a
committed bundle, object, `FORMAT.json`, or other non-temporary path.

Uncommitted terminal bundle residue is not Evidence. Its presence may be reported as an
exact unproven/recovery limit, but it must not be silently counted as a committed event.

## Required automated proof

At minimum, focused tests must prove:

- the opt-in guard skips the hammer matrix in an ordinary run;
- the milestone inventory is non-empty and contains all required Attempt and Capture
  boundary families;
- every pre-send death case produces zero loopback requests;
- server-time independent Attempt verification succeeds before accepting the request;
- every post-send death case produces exactly one request;
- every commitment-claiming candidate after death verifies and scrub reports no corrupt
  committed Evidence;
- post-response/no-Capture cases remain authorized/unresolved and do not trigger retry;
- no-fault control: one request, one Attempt, one Capture, both read back, scrub clean;
- temporary cleanup changes only `.tmp/`;
- sentinel credential scan is clean;
- existing deterministic PF-02 tests and the full ordinary suite remain green.

The test report must state how many fault points ran in the Attempt phase and Capture
phase. A passing assertion that exercised zero points in either phase is invalid.

## Operator acceptance run

After deterministic review, [CHAZ] runs once on the laptop's actual Evidence filesystem
using a new empty path:

    hammer_root="/home/chaz/.local/share/vedaops/observatory/ham01-$(date -u +%Y%m%dT%H%M%SZ)"
    OBSERVATORY_RUN_PAID_GATE_HAMMER=1 \
      uv run pytest -q tests/test_paid_gate_process_death_hammer.py \
      --basetemp "$hammer_root"

Before closure, record:

- the filesystem type and mount target used;
- focused test result and duration;
- Attempt-phase and Capture-phase fault-point counts;
- loopback request-count assertions;
- committed-candidate verification and scrub results;
- credential scan result;
- retained root path for inspection.

Do not export real DataForSEO credentials for this run.

## Scope constraints

One implementation commit; do not amend or push.

The implementer may change only:

- new `tests/test_paid_gate_process_death_hammer.py`;
- `src/observatory/evidence_store.py` only if the hammer exposes an actual Evidence
  ordering/visibility defect requiring the smallest production fix;
- `src/observatory/dataforseo_sandbox.py` only if the hammer exposes an actual
  pre-send/post-response gate defect requiring the smallest production fix;
- this ticket's Status and Implementation report.

If either production file changes, report the exact failing hostile case, why a test-only
change could not make the claim truthful, and the before/after operation order. Do not add
a general fault-injection framework or a production environment variable that kills the
service.

Do not change event schemas or vectors, FORMAT/layout, credentials/settings, dependency
files, derive/PostgreSQL/API behavior, provider endpoints, or another ticket.

## Out of scope

- DataForSEO sandbox or paid network calls
- `api.dataforseo.com`, pricing, budgets, keyword data, or provider-envelope parsing
- power-cut or VM/device crash claims
- multi-process authorization/locking (F7)
- off-host Evidence backup/restore (F6)
- automatic retry, replay lineage, scheduling, or asynchronous task workflows
- provider Outcomes, Observations, Derivation, or API resources
- Ahrefs, Semrush, or a generic provider abstraction

## Verification

Implementation report must include:

- exact parent and child commit;
- exact changed paths;
- milestone inventory and phase counts;
- child exit-code and timeout behavior;
- fault case → Evidence/request/postmortem result mapping;
- no-fault control accounting;
- credential scan evidence;
- `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy`;
- weakest/most fragile part;
- exact unproven limits and any authority disagreement.

Set Status to `review`, not `done`. Only the Project Steward closes HAM-01 after the
operator acceptance run.

## Implementation report

**Parent:** `c67efc6271db6e9a986e188d56e2b3cffb2896dd`  
**Child:** recorded in the implementation commit.

**Changed paths:** `tests/test_paid_gate_process_death_hammer.py` (new), this
ticket (Status + report). No production modules were edited.

**Fault-injection mechanism:** child subprocesses wrap
`EvidenceStore.commit_attempt` / `commit_capture` to mark phase, then wrap
`_create_terminal_directory`, `_install_file`, and `_fsync_dir`. After the
real operation returns, the child calls `os._exit(97)`. No production kill
switch or environment-triggered death exists.

### Milestone inventory

Discovered from a live in-process loopback capture of the concrete store:

- Attempt-phase fault points: **22**
- Capture-phase fault points: **16**
- Required families present: terminal-dir, manifest, bundle-body, COMMITTED,
  fsync-dir for both phases.

### Child exit / timeout

Fault children exit **97**. The no-fault control exits **0**. Child timeout
is 20s; none timed out on the implementer proving run.

### Pre-send / post-send request accounting

- All 22 Attempt-phase deaths: **0** loopback requests.
- All 16 Capture-phase deaths: **exactly 1** request. At request time the
  parent used `inspect_store` and independently verified the sole Attempt
  before the server replied.
- No-fault control: **exactly 1** request.

### Per-fault Evidence / postmortem

After each death, inspect (no mutation) → enumerate commitment-claiming
dirs → verify each → report-only scrub → credential scan → then
`open_store` (`.tmp/` only).

- Attempt-phase: 0 or 1 verified committed Attempt; 0 Captures; scrub
  reports no corrupt committed Evidence; uncommitted terminal residue is
  not counted as Evidence.
- Capture-phase: 1 verified Attempt; 0 or 1 verified Capture; if 0 Capture,
  the Attempt is authorized/unresolved and the matrix does not retry.
- No malformed COMMITTED candidate failed verify.

### No-fault control

1 request, 1 verified Attempt, 1 verified Capture, both read back, scrub
clean, child exit 0.

### Cleanup-only-`.tmp`

`open_store` after inspect removed only paths under `.tmp/`. Committed
bundles, objects, and `FORMAT.json` were unchanged (inode + bytes).

### Credential scan

Sentinel login, password, `Basic` value, and bare token were absent from
Evidence files and child stdout/stderr. Plaintext login/password were
absent from loopback request bytes (the wire carries Authorization as
required by PF-02).

### Commands

- Ordinary `uv run pytest -q`: 602 passed, 1 skipped (matrix), 1 warning
- `uv run ruff check .`: All checks passed
- `uv run mypy`: Success: no issues found in 25 source files
- Implementer proving run (not [CHAZ] closure):
  `OBSERVATORY_RUN_PAID_GATE_HAMMER=1 uv run pytest -q
  tests/test_paid_gate_process_death_hammer.py --basetemp
  /home/chaz/.local/share/vedaops/observatory/ham01-implementer-20260816T150643Z`
  → 2 passed, 1 skipped (opt-in guard), 54.40s; printed
  `HAM-01 fault points: attempt=22 capture=16`

### Production defect

None. The hostile matrix passed against the existing store/transport
protocol. Test-only implementation.

### Weakest / most fragile part

Class-level method wrapping for discovery and children is process-local
and must stay aligned with private store method names. Shared-directory
fsyncs inflate the Attempt-phase count beyond the terminal bundle itself.

### Exact unproven limits

- Not sudden power-loss, device-cache, or VM crash proof
- Not multi-process writer / F7
- Not off-host recovery / F6
- Not TLS, DNS, DataForSEO, or paid-host proof
- Uncommitted terminal residue after pre-COMMITTED death is not recovered
  automatically; it is not treated as Evidence
- Ordinary suite does not run the kill matrix

### Authority

Assigned start `c67efc62…` (HAM-01 authorize) supersedes the ticket’s
pre-filled `672ad53…` (PF-02 close). No other disagreement. PF-03 / paid
transport not implemented.

### Confirmation

No DataForSEO, DNS, paid-host, sandbox, or other public-network call.
Sentinel credentials and `127.0.0.1` loopback only. Zero provider credit.

