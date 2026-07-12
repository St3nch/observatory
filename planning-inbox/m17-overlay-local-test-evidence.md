# M17 Overlay Local Test Evidence — Pending Owner Execution

Status: implementation written; full suite not yet executed
Date: 2026-07-12

The authorized synthetic fixture-backed owned telemetry overlay proof and focused tests are present in the repository.

Required owner-local command:

```powershell
cd C:\dev\observatory
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

No pass is claimed until that command succeeds.

The intended proof scope is synthetic, local, deterministic, and in-memory. It proves only code-path discard behavior. It does not prove secure memory wiping, production infrastructure logging behavior, real private telemetry handling, file/screenshot/export/connector intake, consumer authentication, persistence, database enforcement, production API/MCP behavior, integration, or deployment.
