# M12 Local Test Evidence — 2026-07-10

Status: execution evidence note
Authority: none — evidence note only; milestone closure requires separate decision if used
Milestone: M12 — First Evidence Slice Build
Evidence source: owner-provided PowerShell transcript pasted in project chat
Related commit tested: `4d7609e` / pushed range `ff2f026..4d7609e`

---

## Purpose

Record the first owner-local execution evidence for the C2 first evidence slice tests.

This note preserves the exact command and output reported by the owner so M12 does not rely on vague chat memory.

---

## Execution Context

Reported shell:

```text
PowerShell 7.6.3
```

Reported working directory:

```text
C:\dev\observatory
```

Reported command:

```powershell
python -m unittest discover -s tests
```

Reported result:

```text
............
----------------------------------------------------------------------
Ran 12 tests in 0.003s

OK
```

Reported push after test:

```text
To https://github.com/St3nch/observatory.git
   ff2f026..4d7609e  main -> main
```

---

## Verification Posture

This is owner-local execution evidence.

The connected `ob-dev` tool verified after the push:

```text
## main...origin/main
```

The connected `ob-dev` tool did not independently execute the tests because the connector expects a fixed interpreter at:

```text
C:\dev\observatory\.venv\Scripts\python.exe
```

and `ob-dev.venv_status` reported that interpreter does not exist.

---

## Hammer Coverage Reported by Current Test File

Current test file:

```text
tests/test_c2_first_slice.py
```

Reported local execution covers 12 unittest tests currently intended to exercise:

| Hammer | Coverage posture |
|---|---|
| H1 Scope isolation | local test passed per owner transcript |
| H2 Rights fail-closed | local test passed per owner transcript |
| H3 Retention enforcement | local test passed per owner transcript |
| H5 No strategy/recommendation storage | local test passed per owner transcript |
| H6 Observation envelope validation | local test passed per owner transcript |
| H9 Freshness / point-in-time claim-use warning | local test passed per owner transcript |
| H12 Raw archive integrity if raw support is included | local test passed per owner transcript |
| H15 Evidence ID / citation integrity | local test passed per owner transcript |
| H18 Hostile weird input | local test passed per owner transcript |
| H19 Append-only observations | local test passed per owner transcript |
| H21 Audit-first enforcement | local test passed per owner transcript |
| C2 happy path / admission spine | local test passed per owner transcript |

H22 rollback/recovery expectations remain planning-level unless/until a specific executable proof is added.

---

## Boundary Confirmation

This evidence does not indicate any of the following occurred:

```text
provider calls
provider clients
DataForSEO pulls
Ahrefs/Semrush work
provider admission
customer data
marketplace scraping
browser-extension capture
API/MCP exposure
dashboard work
recurring capture
strategy/recommendation storage
report generation
manual capture as production capture
```

The reported command is local unittest execution only.

---

## M12 Use

This evidence may support a later M12 review.

It should not, by itself, close M12.

Before M12 closure, the project should still review:

- whether the test assertions are sufficient for each claimed hammer;
- whether H22 needs an executable proof or remains deferred/planning-level;
- whether local test execution should be repeated through a repo-managed `.venv` if connector-side verification becomes necessary;
- whether documentation should distinguish owner-local pass from connector-verified pass.

---

## Anti-Drift Notes

Do not infer from this note that:

- M12 is closed;
- hammers are globally accepted for all future surfaces;
- provider/customer/API/dashboard/marketplace/recurring-capture work is authorized;
- manual capture is production-approved;
- tests were independently executed by `ob-dev`.

---

## Result

```text
Owner-local M12 unittest run reported: 12 tests passed.
Repo push verified clean/synced after the reported run.
```
