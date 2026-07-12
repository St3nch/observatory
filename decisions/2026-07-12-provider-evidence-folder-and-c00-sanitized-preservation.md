# Decision — Provider Evidence Folder and C00 Sanitized Preservation

Status: accepted decision
Authority: owner-approved audit-response implementation under the M14 planning boundary
Date: 2026-07-12
Related audit findings: F-02, F-06

## Decision

Create `providers/` as the governed home for committed, sanitized provider-admission and provider-shape evidence.

Preserve the reviewed M13 DataForSEO C00 artifacts that contain no raw result payload, credentials, account secrets, customer data, or payment details.

The ignored operational path remains local:

```text
probe-evidence/
```

The committed preservation path is:

```text
providers/dataforseo/evidence/2026-07-12_C00_145948Z-f0b5410c/
```

## Allowed committed artifacts

- sanitized request manifest;
- response-status and count summary;
- normalized field inventory;
- item-type summary;
- cost reconciliation;
- purge proof;
- sanitized attempt ledger snapshot;
- README describing provenance and limits.

## Excluded

- `02-raw-response.json`;
- credentials or authorization headers;
- provider account identifiers;
- payment details;
- customer/private data;
- raw SERP result values;
- the consumed owner-confirmation phrase.

## Boundary

This decision preserves evidence only. It does not authorize another provider request, provider execution, recurring capture, Postgres, schema, migrations, API/MCP implementation, customer data, or strategy/recommendation storage.
