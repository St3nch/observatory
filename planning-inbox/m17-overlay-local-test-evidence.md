# M17 Overlay Local Test Evidence

Status: passed — bounded synthetic fixture/in-memory suite
Date: 2026-07-12
Implementation commit: `7cdcdc7cbaeff7c68c30653f91231d7fe3fe7964`
Test-correction commit: `04ef29c980d9c655acc739693b944fa5b6a6faeb`

The owner executed the required full suite locally:

```powershell
cd C:\dev\observatory
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

The first run exposed one false-positive safety test caused by Python's automatic `__cached__` module attribute. The test was corrected to inspect only project-defined mutable globals. The owner reran the full suite.

Observed final result:

```text
Ran 184 tests in 0.181s
OK
```

Expected blocked-path messages from preserved M13 safety tests appeared. No provider request or spend was authorized or executed.

Proof classification:

```text
proof_class: mixed_suite
execution_surface: synthetic_fixture_in_memory_local
proof_strength: bounded_enforcement_proof
```

This proves the committed local code-path boundaries for synthetic overlay inputs: no returned overlay values, no evidence promotion, no cross-scope access, and explicit discard/no-storage behavior. It does not prove secure memory wiping, production infrastructure logging behavior, real private telemetry handling, file/screenshot/export/connector intake, consumer authentication, persistence, database enforcement, production API/MCP behavior, integration, or deployment.
