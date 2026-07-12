# DB-1 Typed-Read Corrective Proof

Status: implementation complete; owner-local full-suite proof pending
Date: 2026-07-12
Authority: `decisions/2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md`
Audit source: `audits/observatory-post-v1-pre-database-deep-audit-2026-07-12.md`

## Corrective scope

This bounded DB-1 correction addresses:

- N-01 silent total-result truncation;
- N-08 missing cursor expiration;
- N-09 stale Hermes lineage statement;
- N-11 accidental nested authorization coupling;
- N-13 hard-coded consumer-promotion flag;
- N-14 undocumented M15-to-M14 claim-intent translation.

It also updates the typed-read and SearchClarity proof contract versions to `0.1.1`.

## Implemented behavior

### Ceiling disclosure

The reader now counts all otherwise-visible evidence before applying `MAX_TOTAL_RESULTS`. Any evidence omitted by the total ceiling remains represented in:

```text
truncated: true
omitted_evidence_unit_count: <accurate remaining visible count>
```

A hostile test temporarily creates an over-ceiling population and asserts six omitted evidence units after a two-unit first page.

### Cursor expiration

Cursor payloads now carry `expires_at`, defaulting to a 300-second fixture TTL. Expired cursors fail closed as `blocked_filter`. Scope binding, caller binding, request-type binding, claim-intent binding, contract-version binding, and HMAC signature checks remain.

The signing key remains a fixture constant. Audit finding N-12 remains assigned to the future managed-secret gate before database-backed or network-exposed reads.

### Authorization composition

`freshness_check` now authorizes only its declared outer request type and calls an internal unit lookup helper rather than invoking the public `evidence_lookup` handler. A `freshness_only` fixture grant proves that no hidden `evidence_lookup` grant is required.

### Consumer promotion

`consumer_promotion_required` is now computed. It is true for:

```text
comparative_observation
coverage_statement
absence_statement
internal_governance_support
```

Direct historical/current observation use remains false in this bounded prototype.

### Lineage and claim-intent mapping

The typed-read contract now records the completed Hermes lineage review rather than preserving a false open gap.

The SearchClarity proof contract now explicitly records these conservative adapter mappings:

```text
provider_metric_statement -> historical_observation
ai_geo_sampled_observation -> historical_observation
```

The mapping is evidence-selection only and may not strengthen claims, erase original intent, or authorize customer-facing meaning.

## Files changed

```text
contracts/typed-read-api-mcp-v0-1.md
contracts/searchclarity-proof-workflow-v0-1.md
src/observatory_typed_read_prototype/models.py
src/observatory_typed_read_prototype/reader.py
src/observatory_typed_read_prototype/fixtures.py
src/observatory_searchclarity_proof/models.py
tests/test_typed_read_hostile_paths.py
```

## Owner-local proof attempts

### Attempt 1 — failed on stale expectation

The owner ran the full suite after commit `e56af0e29fde4bbff43a22073b33549c8ae984dd`.

Result:

```text
Ran 188 tests in 0.205s
FAILED (failures=1)
```

Failure:

```text
test_typed_read_contract.TypedReadContractTests.test_coverage_is_sorted_and_evidence_only
```

The stale assertion expected `consumer_promotion_required` to remain false for `coverage_statement`. The v0.1.1 contract now intentionally classifies coverage-bearing output as meaning-bearing, so the implementation's `true` result was correct and the old test expectation was wrong. The test was corrected to require `true`.

### Required rerun

Run from `C:\dev\observatory`:

```powershell
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

Expected minimum:

```text
188 tests
OK
```

The expected count is 184 prior tests plus four new hostile/corrective tests.

## Proof ceiling

This correction proves fixture/in-memory typed-read behavior only. It does not prove database queries, database authorization, managed secrets, key rotation, network cursors, production pagination, or persistence.

## Non-authorizations

```text
No Postgres creation.
No DDL.
No migration files or execution.
No database credentials.
No provider calls or real ingestion.
No production API/MCP.
```
