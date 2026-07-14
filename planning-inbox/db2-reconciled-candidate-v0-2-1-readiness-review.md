# DB-2 Reconciled Candidate v0.2.1 Readiness Review

Status: replacement planning review after independent rejection; not acceptance, closure, or DB-3 authority
Date: 2026-07-13
Milestone: DB-2 - Physical Data-Contract Freeze Reconciliation
Authority: none; owner/steward review material only

## Prior candidate disposition

Candidate v0.2.0 failed independent ChatGPT desktop steward review. It is not
approved for commit or owner acceptance. Its untracked readiness review was removed
and is rejected as current proof.

The steward found:

- accepted `capture_id` authority was contradicted;
- accepted M10, freshness, and claim-safety concepts were missing or grouped vaguely;
- changing concepts referred to unspecified transition histories;
- the post-v1 roadmap repeated the current-review-target block;
- the authority checker accepted status through an unsafe substring test and was
  bound to the failed version/review.

## Exact review target

```text
canonical candidate: planning-inbox/db2-physical-data-contract-freeze-specification.md
candidate version: 0.2.1
candidate SHA-256: 7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891
HEAD: ef1c1b6be829c406b58ec0d0062b5b13e208dac2
branch: main
upstream: origin/main
ahead / behind: 2 / 0
```

The candidate is a dirty-working-tree planning artifact. It is not authority.
`audits/kaizen_to_slash_goal_prompt.md` remains unrelated, untouched, and untracked.

## Capture-identity conflict resolved

Accepted sources:

- `contracts/evidence-id-citation.md` defines `capture_id` as a capture event or
  capture attempt that groups provider/API/manual attempts and explains zero, one,
  or many observations.
- `contracts/capturepackage-v0-1.md` requires both `capture_package_id` and
  `capture_id` in the CapturePackage shape.

Candidate v0.2.1 therefore defines:

```text
capture_package_id: identity of the CapturePackage admission envelope
capture_id: identity of the accepted capture event/attempt under that package
capture_attempt_id: unresolved inactive rename/alias proposal; no active namespace,
                    facts, relationships, reads, or behavior; owner ruling required
```

The v0.2.0 package-alias rule is removed. Package 1:N capture cardinality and all
provider, candidate, raw, time, transition, and hammer relationships now use the
accepted `capture_id` meaning.

## Accepted concepts added or made explicit

### M10 responsibilities

- `observed_artifact_reference` - `durable`
- validation-failure vocabulary - `versioned`
- validation result - `append_only`
- `validation_status` - `derived`
- `rejection_reason` - `append_only`

### Freshness and volatility

- `captured_at` - `append_only` immutable target fact
- `provider_reported_time` - `append_only` provider-attributed fact
- observation age - `derived`
- age-band vocabulary - `versioned`
- `age_band` - `derived`
- `freshness_status` - `derived`
- `volatility_class` - `derived` from governed assignment/policy
- update-window input - `ephemeral`

### Claim safety

- claim-intent vocabulary - `versioned`
- `claim_intent` selection and claim input - `ephemeral`
- `claim_support` - `derived`
- historical/current/comparative/absence/provider-metric/AI-GEO/marketplace claim
  inputs - `ephemeral`
- predictive/causal/recommendation claims and accepted conclusions - `forbidden`
- claim-use, freshness, provider-attribution, sample-bound, absence,
  incomparability, rights/retention warnings, and consumer-promotion requirement -
  `derived`

### Additional accepted-contract concepts

Source-admission status, rights/retention bases and deadlines, owning-consumer label,
capture method, operator intent, approval reference, ceilings, stop conditions,
raw-support status, panel item, provider recipe and metric facts, comparison context
and results, consumer request, evidence pack, coverage/blind spots, caller class,
authorization grant, cursor, pagination/truncation, overlay freshness, and overlay
discard status now have explicit classifications and dossier boundaries.

## Lifecycle-transition completion

Candidate v0.2.1 names base facts, append-only transition concepts, transition IDs,
target cardinality, event vocabularies, write authority, audit behavior, retention,
derived current state, and hammers for:

- scope;
- observed artifact reference;
- source family and source-family assignment;
- capture instrument;
- query panel and panel run;
- CapturePackage and capture event/attempt;
- provider identity and provider testimony;
- candidate and admitted observation;
- evidence identity and citation handle;
- raw manifest, raw payload identity, and opaque artifact token;
- shape fingerprint and parser-support posture;
- freshness and volatility assignments.

Rights/retention assignment histories, admission decisions, drift review, audit,
security, and raw support/purge transitions remain separately explicit in the main
concept register. No mutable current-state record is authorized.

## Roadmap and authority-guard corrections

- `POST_V1_DATABASE_ROADMAP.md` now has exactly one current-review-target block,
  pointing to v0.2.1 and this review.
- The authority checker uses exact expected status lines for the candidate, this
  review, and the historical correction-disposition record.
- It binds exact version and SHA-256, rejects a reappearing v0.2.0 current review,
  verifies capture identity and required concept markers, and requires exactly one
  roadmap target block.
- Deterministic tests cover these guards.

## Semantic re-audit result

| Area | Result |
|---|---|
| Accepted DB-1 contract representation | pass; accepted input reconciliation and remainder audit cover the full read path |
| C-01 through C-12 defensibility | pass; all twelve retained with corrected boundaries |
| Singular classifications / separate qualifiers | pass; exact primary-class checks cover the newly reconciled concepts |
| Base facts / transitions / derived state | pass; named transition mechanisms and derived states are explicit |
| Capture identity | corrected |
| M10/freshness/claim-safety coverage | corrected |
| Rights/retention target coverage | pass; target bindings, bases, deadlines, histories, and loss behavior are explicit |
| Raw ownership, disagreement, overlays, forbidden persistence | pass; ownership and non-persistence boundaries remain fail-closed |
| Typed-read locator/credential exclusion | pass; safe fields only, with locators and credentials forbidden |
| H1-H22 `defined_only` mappings | pass; exactly 22 definitions remain non-executed proof mappings |
| Physical design or implementation authority | absent; no schema, SQL/DDL, migration, role, database, or implementation artifact added |

## Validation evidence

Interpreter: `C:\Users\Stench\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`

- `...\python.exe tools/check_authority_sync.py --json` - exit 0; passed with no
  errors; DB-1 remains last trusted and DB-2 remains reconciliation-only.
- `...\python.exe -m unittest tests.test_authority_sync` - exit 0; 6 tests passed.
- `...\python.exe -m unittest discover -s tests` - exit 0; 194 tests passed.
- `git diff --check` - exit 0; no whitespace errors.
- `git status --short` - exit 0; only the DB-2 review package plus the protected
  unrelated untracked audit are dirty; nothing is staged.
- `git diff --cached --name-only` - exit 0; empty.
- SHA-256 recomputation - exit 0;
  `7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891`.
- Targeted `rg`/PowerShell semantic checks - exit 0 as a combined assertion set:
  rejected-review path absent as a file/current pointer; one roadmap target;
  accepted capture meanings; one fail-closed `capture_attempt_id` disposition;
  complete M10/freshness/claim-safety rows with exact primary classes; no compound
  primary classification in a dossier row; append-only mutation forbidden; retired
  DB-3/DB-4 paths absent except checker guards; no physical schema/SQL/migration
  artifact; protected audit remains untracked and was excluded from every edit.

## Readiness disposition

```text
disposition: ready for another independent steward review; not owner acceptance
DB-2 accepted: no
DB-2 closed: no
DB-3 authorized: no
implementation authorized: no
```

## Exact three-decision owner gate

Only after another independent steward review may the owner separately decide:

1. Accept or reject the exact v0.2.1 candidate identified above.
2. Close or continue DB-2.
3. Authorize or refuse preparation of fresh DB-3 planning.

No decision automatically answers another. None authorizes DB-4, PostgreSQL,
databases, roles, credentials, schema, SQL/DDL, migrations, database tools,
implementation, persistence, providers, capture, customer data, raw storage,
recurring execution, or production.
