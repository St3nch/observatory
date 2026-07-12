# Decision: M12 First Evidence Slice Closure

Status: accepted decision
Authority: owner milestone closure / roadmap transition
Date: 2026-07-10
Milestone: M12 — First Evidence Slice Build
Closure basis: `planning-inbox/m12-first-slice-closure-readiness-review.md`

---

## Decision

M12 is closed.

M13 — Provider Admission and Controlled Pull Plan is now active.

M12 accepts the bounded first evidence slice build for:

```text
C2 — Controlled Public Manual Observation Package
```

This decision accepts only the local, fixture-based C2 first-slice proof.

It does not accept provider admission, provider calls, paid pulls, API/MCP exposure, dashboard work, customer-data handling, recurring capture, report generation, or broad Observatory implementation.

---

## Accepted M12 Build Surface

M12 accepts these implementation artifacts as the first local evidence-slice proof:

```text
src/observatory_c2/__init__.py
src/observatory_c2/c2.py
tests/test_c2_first_slice.py
pyproject.toml
tests/README.md
```

The accepted build surface is:

- pure local Python;
- stdlib-only;
- fixture-based;
- in-memory only;
- no database connection;
- no migration;
- no provider client;
- no network call;
- no API/MCP exposure;
- no dashboard;
- no customer data;
- no strategy/recommendation store.

---

## Accepted Test Evidence

M12 closure accepts owner-local test evidence recorded in:

```text
planning-inbox/m12-local-test-evidence-2026-07-10.md
```

Owner-local command:

```powershell
cd C:\dev\observatory
python -m unittest discover -s tests
```

Owner-reported result:

```text
Ran 13 tests in 0.004s
OK
```

The repo was verified clean/synced after the owner pushed the tested commit range.

The connected `ob-dev` tool did not independently execute the tests because the repo has no `.venv` at the connector-expected interpreter path.

This evidence is accepted as owner-local M12 execution evidence for the bounded C2 slice only.

---

## Accepted Hammer Scope

M12 accepts local C2 hammer evidence for:

```text
H1  Scope isolation
H2  Rights fail-closed
H3  Retention enforcement
H5  No strategy/recommendation storage
H6  Observation envelope validation
H9  Freshness / point-in-time claim-use warning
H12 Raw archive integrity if raw support is included
H15 Evidence ID / citation integrity
H18 Hostile weird input
H19 Append-only observations
H21 Audit-first enforcement
H22 Rollback/recovery expectations
```

Acceptance scope:

```text
These hammers are accepted only for the bounded local C2 fixture implementation.
```

This does not prove all future Observatory surfaces.

---

## Scope Caveats

M12 closure does not imply:

- provider evidence is admitted;
- provider calls are authorized;
- paid pulls are authorized;
- raw payload retention is broadly allowed;
- report-safe citation handles are settled;
- customer-facing workflows are ready;
- API/MCP read tools are ready;
- database persistence exists;
- migrations exist;
- manual capture is production-approved;
- recurring capture is approved;
- dashboards are approved;
- strategy/recommendation storage is approved.

---

## M13 Activation Boundary

M13 may begin provider admission and controlled pull planning only.

M13 may plan:

- provider admission document;
- rights/retention/cost gate confirmation;
- controlled pull recipe;
- cost ceiling;
- stop conditions;
- raw payload handling plan;
- no-customer-data posture;
- no-recurring-capture posture;
- no-dashboard/report/API/MCP exposure posture.

M13 must not perform:

```text
provider calls
paid provider pulls
provider purchases
Ahrefs/Semrush spend
bulk capture
recurring capture
customer data handling
API/MCP exposure
dashboard work
report generation
strategy/recommendation storage
```

---

## Non-Authorization Boundary

This decision does not authorize:

```text
DataForSEO calls
Ahrefs calls
Semrush calls
provider purchases
paid pulls
provider admission execution
bulk capture
recurring capture
customer data handling
marketplace scraping
browser-extension capture
API/MCP exposure
dashboard work
customer-facing reports
strategy/recommendation storage
broad implementation beyond the accepted local C2 proof
```

---

## Source Inputs

This decision closes M12 using:

- `decisions/2026-07-10-m11-foundation-closure.md`
- `planning-inbox/m12-local-test-evidence-2026-07-10.md`
- `planning-inbox/m12-first-slice-closure-readiness-review.md`
- `src/observatory_c2/__init__.py`
- `src/observatory_c2/c2.py`
- `tests/test_c2_first_slice.py`
- `tests/README.md`
- `hammers/acceptance-gate-policy-v0-1.md`

---

## Closure Result

```text
M12 closed.
M13 active.
```

M13 is active for provider admission and controlled pull planning only, under the roadmap boundaries.
