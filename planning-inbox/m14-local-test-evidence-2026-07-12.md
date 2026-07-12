# M14 Local Test Evidence — 2026-07-12

Status: owner-local execution evidence
Authority: bounded test evidence only
Milestone: M14 planning / post-M13 audit correction Batch A

---

## Command

```powershell
cd C:\dev\observatory
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

## Owner-Reported Result

```text
Ran 128 tests in 0.151s
OK
```

## Relevant Proof

The run occurred after:

- disarming `LIVE_EXECUTION_AUTHORIZED` after M13 closure;
- removing the consumed replacement-request branch;
- reconciling package/config authority statements;
- updating root phase authority to M14 planning.

Observed blocked-path output included the legacy fixture guard, immutable-request confirmation mismatch, invalid probe ID, blocked no-network preflight, and wrong-hash purge rejection.

No provider request was made. No HTTP 401 appeared. No spend occurred.

## Scope Caveat

This result proves the committed local Python test suite for the current fixture, in-memory, filesystem, and mocked-provider surfaces. It does not prove Postgres, transaction, concurrency, API/MCP, production deployment, or future provider-execution enforcement.
