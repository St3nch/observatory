# M17 Owner-Ruling Proposals

Status: planning / owner-decision proposal
Authority: none until accepted in `decisions/`
Milestone: M17
Date: 2026-07-12

---

## Purpose

Present the minimum rulings required before the M17 owned telemetry overlay proof contract can be accepted or any bounded proof implementation can be authorized.

---

## OR-F2 — Internal first-party telemetry posture

Proposed ruling:

```text
Synthetic internal telemetry follows the same no-storage overlay law as synthetic customer first-party telemetry.
```

Owner-controlled or internal provenance does not create an Observatory-storage exception. Real internal telemetry remains separately gated.

## M17-R1 — Real-input boundary

Proposed ruling:

```text
M17 proves behavior with synthetic in-memory fixtures only.
```

No real customer analytics, owner-private telemetry, account identifiers, exports, URLs, screenshots, files, credentials, or connector data are admitted.

## M17-R2 — Discard-proof threshold

Proposed ruling:

For the bounded local proof, discard is considered proven only when tests show:

- no file, database, network, subprocess, environment-secret, or external-repository access;
- no mutable overlay cache or registry;
- fixtures unchanged after use;
- no overlay value in proof records or logs;
- deterministic response construction;
- explicit `overlay_persisted: false` and `overlay_discard_status: discarded_after_response_build`.

This does not claim production memory-erasure or infrastructure logging proof.

## M17-R3 — Retained manifest posture

Proposed ruling:

```text
No overlay-derived manifest survives the read call.
```

Do not retain values, hashes, field inventories, external overlay references, alignment output, or derived private summaries. Repository proof records may retain only non-payload execution metadata.

## M17-R4 — Intervention timeline posture

Proposed ruling:

```text
Synthetic intervention timelines may support temporal before/after alignment only.
```

They may not establish or store causality, recommendations, tasks, report prose, or accepted conclusions.

## M17-R5 — Files and screenshots

Proposed ruling:

```text
Screenshots, CSV/PDF exports, URLs, files, and external references remain blocked in M17.
```

The first proof implements no parser, upload path, connector, or screenshot/file reader.

## M17-R6 — Overlay identity

Proposed ruling:

```text
Overlay inputs never receive Observatory evidence, observation, capture, raw-payload, citation, or scope identity.
```

A request-local external reference may exist during the call but must not survive as persisted metadata.

## M17-R7 — Alignment output ceiling

Proposed ruling:

M17 may return only:

- temporal/value alignment facts from synthetic fixtures;
- freshness and incomparability warnings;
- coverage/blind-spot context;
- explicit no-storage/discard status;
- consumer-promotion requirements.

It may not return causal conclusions, recommendations, tasks, report prose, recapture instructions, or customer-facing authorization.

## M17-R8 — Bounded proof eligibility

After contract and hostile-path acceptance, M17 may propose one local deterministic fixture-backed proof.

The proof remains:

- synthetic;
- in-memory;
- local-only;
- no real private data;
- no files/screenshots/exports;
- no persistence or caching;
- no network/provider/connector calls;
- no Postgres;
- no production API/MCP;
- no consumer integration or reports.

Implementation requires separate exact owner authorization.

---

## Recommended owner decision bundle

```text
ACCEPT OR-F2 internal telemetry follows no-storage overlay law
ACCEPT synthetic-only M17 input boundary
ACCEPT bounded local discard-proof threshold and its limitations
ACCEPT no retained overlay-derived manifest
ACCEPT intervention timelines for temporal alignment only
ACCEPT files/screenshots/exports remain blocked
ACCEPT no Observatory identity for overlay inputs
ACCEPT alignment-output ceiling and mandatory consumer promotion
ACCEPT bounded M17 proof eligibility, not implementation
```

Do not combine implementation authorization with this ruling bundle.

---

## Still deferred

- real customer first-party analytics;
- real owner/internal telemetry;
- production discard guarantees;
- file/screenshot/export intake;
- connector-based overlay delivery;
- persistent non-private overlay manifests;
- customer-facing overlay wording;
- Postgres, schema, migrations, production API/MCP, and production integrations.
