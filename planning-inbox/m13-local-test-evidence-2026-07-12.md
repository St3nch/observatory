# M13 Local Test Evidence — 2026-07-12

Status: owner-local execution evidence
Authority: evidence only — not funding approval, credential approval, provider execution approval, or M13 closure
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Command

```powershell
cd C:\dev\observatory
python -m unittest discover -s tests
```

## Owner-Reported Results

Initial fixture-only proof:

```text
Ran 67 tests in 0.070s
OK
```

Expanded campaign-catalog proof:

```text
Ran 105 tests in 0.028s
OK
```

Expanded paid-evidence review-package proof:

```text
Ran 114 tests in 0.110s
OK
```

Guarded C00 live-execution readiness proof:

```text
Ran 126 tests in 0.148s
OK
```

The latest full run includes the existing C2 first-slice tests, DataForSEO probe hostile paths, campaign catalog tests, evidence-package organization tests, and guarded live-execution tests covering credential handling, duplicate reservation, timeout/no-retry behavior, fixed endpoint construction, authorization gating, and automatic evidence packaging.

## Observed Fail-Closed Output

The run visibly confirmed that the CLI remained blocked for real execution and reported these blockers:

```text
funding_not_authorized
network_execution_not_authorized
exact_price_missing
account_limits_not_recorded
evidence_root_not_git_ignored
credentials_missing
```

It also showed:

```text
network_execution_authorized: false
maximum_expected_cost_usd: 0.1
api_request_ceiling: 1
billable_task_ceiling: 1
retry_ceiling: 0
polling_ceiling: 0
repeat_ceiling: 0
```

The immutable request hash observed in the run was:

```text
f0b5410c5cc490b64ec4bb471a92c24647dccf432962fcd952c4070b03b2c4c9
```

The duplicate-prevention key observed in the run was:

```text
ba0ecb2b81b3bfb4cc90a3311a285ca02fc17e165ff58ea49ae6768f7b96970d
```

## Regression Fix Included

The first owner-local run exposed one fixture failure in `test_purge_records_hash_and_deletes` because `is_within_evidence_root()` captured the original `EVIDENCE_ROOT` in a Python default argument before the test patched it.

The implementation was corrected so the active evidence root is resolved at call time. The outside-root purge guard remains covered separately.

Commit containing the fix:

```text
98a796f Fix dynamic probe evidence root
```

The complete suite then passed.

## Evidence Limits

This is owner-local output pasted into project chat and recorded by the steward.

It is not:

```text
connector-executed test proof
provider-call proof
pricing proof
funding proof
credential proof
raw provider evidence
```

## Disposition

```text
Fixture-only implementation tests: passed locally
Latest tests run: 126
Failures: 0
Errors: 0
Paid-evidence organization tests: passed
Guarded live-execution tests: passed
Network execution: still disabled
Account funding and controls: evidenced separately
Provider request: still not authorized
```
