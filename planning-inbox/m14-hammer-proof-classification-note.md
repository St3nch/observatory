# M14 Hammer Proof Classification Note

Status: accepted planning clarification pending later contract/hammer integration
Authority: classification guidance only; does not reopen M8–M13
Milestone: M14 — Typed Read API / MCP Contract and Prototype
Date: 2026-07-12

---

## Purpose

Preserve the value of Observatory's broad hostile-path test system without implying that every passing test proves the same kind of hardening.

The term `hammer` remains reserved for high-consequence hostile-path proof. Ordinary correctness checks should use ordinary labels.

## Test Classes

```text
substrate_hammer
integration_hammer
access_boundary_hammer
contract_acceptance
semantic_safety
static_conformance
unit_test
```

## Execution Surfaces

```text
fixture
in_memory
filesystem
provider_mock
live_provider
database
API_or_MCP
production_like
```

## Proof Strength

```text
illustrative
bounded
enforcement_proof
```

## Classification Rule

A test earns hammer status only when failure could cause a high-consequence boundary breach, including:

- corrupted, overwritten, or unrecoverable evidence;
- cross-scope leakage;
- unauthorized spend or provider execution;
- rights or retention violation;
- missing or false provenance;
- credential, raw-pointer, or protected-content exposure;
- silent provider drift or parser corruption;
- conclusions or strategy entering the evidence store;
- misleading evidence leaving a read boundary;
- audit, rollback, or recovery failure.

Tests that only prove normal business logic, field formatting, stable serialization, or minor wording remain useful but should not be labeled as hammers.

## Existing Evidence

M8–M13 remain closed. Existing tests keep the proof scope under which they were accepted.

Future references should annotate the actual proof class, execution surface, and strength. Example:

```text
H19 append-only
proof_class: substrate_hammer
current_surface: in_memory
current_strength: bounded
persistence_enforcement_status: blocked_not_implemented
```

```text
H9 freshness caveat
proof_class: contract_acceptance
current_surface: fixture
current_strength: bounded
```

No fixture or in-memory result may be restated later as database, transaction, MCP/API, or production enforcement proof.
