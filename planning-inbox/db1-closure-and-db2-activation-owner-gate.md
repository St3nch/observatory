# DB-1 Closure and DB-2 Activation Owner Gate

Status: owner-ready decision proposal; not accepted authority
Date: 2026-07-13

## Purpose

Provide one exact decision phrase that closes DB-1 and, only if the owner chooses, separately activates DB-2 planning.

## Option A — Close DB-1 and activate DB-2

```text
ACCEPT HAMMER MATRIX v0.2
ACCEPT ACCEPTANCE GATE POLICY v0.2
ACCEPT PER-HAMMER RESULT REGISTER CONTRACT v0.1
ACCEPT DB-2 PHYSICAL DATA-CONTRACT FREEZE v0.1

CLOSE DB-1 — POST-V1 AUDIT RECONCILIATION AND RULING CLOSURE
ACTIVATE DB-2 — PHYSICAL DATA-CONTRACT FREEZE

DB-2 AUTHORIZES LOGICAL CONTRACT FREEZE AND RECONCILIATION ONLY.
DB-2 DOES NOT AUTHORIZE POSTGRESQL CREATION, ROLES, CREDENTIALS, DDL,
MIGRATION FILES, MIGRATION EXECUTION, DISPOSABLE DATABASES, REAL-POSTGRES
HAMMERS, SYNTHETIC OR REAL PERSISTENCE, PROVIDER CALLS, CUSTOMER DATA,
PRODUCTION API/MCP, RECURRING CAPTURE, OR STRATEGY/RECOMMENDATION STORAGE.
```

## Option B — Close DB-1 without activating DB-2

```text
ACCEPT HAMMER MATRIX v0.2
ACCEPT ACCEPTANCE GATE POLICY v0.2
ACCEPT PER-HAMMER RESULT REGISTER CONTRACT v0.1
ACCEPT DB-2 PHYSICAL DATA-CONTRACT FREEZE v0.1 AS PREPARED NEXT-GATE MATERIAL

CLOSE DB-1 — POST-V1 AUDIT RECONCILIATION AND RULING CLOSURE
DO NOT ACTIVATE DB-2
```

## Option C — Return package for revision

```text
RETURN DB-1 CLOSURE PACKAGE FOR REVISION

Required revisions:
- [owner supplies exact revisions]

DB-1 REMAINS ACTIVE.
DB-2 REMAINS INACTIVE.
```

## Effect of Option A

Option A would authorize only DB-2 work defined by `POST_V1_DATABASE_ROADMAP.md`:

- reconcile and freeze one logical data contract;
- classify every concept;
- finalize identity, lifecycle, provenance, scope, rights, retention, write-authority, read-exposure, and hammer implications;
- preserve the forbidden-persistence register;
- prepare owner acceptance for DB-3 planning.

It would not authorize physical schema work or database execution.

## Final rule

```text
Closing DB-1 and activating DB-2 are separate decisions even when stated together.
No database permission is hidden inside either phrase.
```
