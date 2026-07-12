# M13 DataForSEO Probe Implementation Candidate Review

Status: implementation candidate review
Authority: none — evidence/review only; not funding or provider execution approval
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12

---

## Result

The bounded fixture-only DataForSEO probe safety cage has been implemented as a candidate under the accepted no-network owner ruling.

Implemented paths:

```text
src/observatory_dataforseo_probe/__init__.py
src/observatory_dataforseo_probe/core.py
src/observatory_dataforseo_probe/cli.py
tests/test_dataforseo_probe.py
```

Supporting changes:

```text
.gitignore — adds probe-evidence/
pyproject.toml — records M13 fixture-only posture and disabled funding/network/Postgres/schema state
```

## Enforced Boundaries

The implementation binds one immutable recipe, one endpoint, one task, one request, zero retries, zero polling, zero repeats, a $0.10 ceiling, duplicate-key construction, credential-presence checks without serialization, response classification, shape fingerprinting, local evidence-root checks, and raw purge proof.

Network execution is deliberately impossible:

```text
NETWORK_EXECUTION_AUTHORIZED = False
execute_request(...) always raises ProbeBlocked
```

No HTTP library or provider client is present.

## Test Candidate

`tests/test_dataforseo_probe.py` covers recipe immutability, missing/extra/cost-bearing fields, authority gates, price ceiling, duplicate detection, evidence-root enforcement, credential redaction, request/task/retry/polling ceilings, response/error classification, shape fingerprinting, raw hashing/purge, retention deadlines, CLI blocking, and permanent no-network behavior.

## Verification Result

The owner ran:

```powershell
cd C:\dev\observatory
python -m unittest discover -s tests
```

Final result after the dynamic evidence-root regression fix:

```text
Ran 67 tests in 0.070s
OK
```

The first run correctly exposed one fixture defect involving a Python default argument that captured the original evidence root before patching. Commit `98a796f` corrected the function to resolve the active root at call time. The separate outside-root purge test remains in place.

Detailed evidence is recorded in:

```text
planning-inbox/m13-local-test-evidence-2026-07-12.md
```

Implementation-readiness disposition:

```text
fixture-only implementation accepted as passing local proof
network execution remains disabled
funding and provider execution remain separately gated
```

## Still Forbidden

```text
DataForSEO credits
use of existing credits
real credentials
network requests
provider tasks
raw provider capture
Postgres
schema
migrations
API/MCP
dashboard
customer data
recurring capture
```

## Disposition

```text
Fixture-only implementation accepted as passing local proof.
Authority boundaries encoded and regression-tested.
67 tests passed.
Next gate: owner-controlled funding, exact price verification, account controls, and separate one-request execution approval.
Provider machine remains off.
```
