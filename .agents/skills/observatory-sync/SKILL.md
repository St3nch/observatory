---
name: observatory-sync
description: Synchronize with The Observatory repository before orientation, planning, implementation, review, milestone changes, database work, MCP work, provider work, or any nontrivial edit. Use it to prove the active authority gate, detect drift, and stop unauthorized work.
---

# Observatory Sync

Use this workflow before nontrivial Observatory work.

## Procedure

1. Confirm the working directory is the Observatory Git root.
2. Run `python tools/check_authority_sync.py`.
3. Read the mandatory root sequence in `AGENTS.md` exactly in order.
4. Read the active additional path in `NEXT_SESSION_HANDOFF.md`.
5. Treat planning-inbox, audit, readiness-review, proposal, and candidate files as non-authority unless an accepted, unsuspended decision promotes them.
6. Produce the synchronization proof below.
7. Stop if files are missing, the checker fails, authority disagrees, or the requested work exceeds the active gate.

## Synchronization proof

Report:

```text
repository root:
files read:
last trusted completed milestone:
active milestone or recovery gate:
allowed work:
forbidden work:
missing files:
contradictions:
implementation authorized: yes/no
```

Do not replace missing evidence with chat memory.

## Mutation gate

Before editing:

- name the owning document;
- classify the edit under `ROADMAP_RULES.md`;
- identify the accepted decision or active milestone that permits it;
- preserve explicit non-authorizations;
- verify that a candidate is not being promoted accidentally.

When milestone state legitimately changes, update the current-state documents, machine-readable project status, and authority-sync checker together.

## Tool boundary

Use native Codex tools for ordinary PowerShell, filesystem, Git, tests, and review. Do not use old `ob-dev` Git tools. Use `ob-dev-mcp` only for its explicitly bounded surface.

Never infer database, migration, provider-spend, destructive, customer-data, or production authority from tool availability.

## Completion

Run:

```powershell
python tools/check_authority_sync.py
python -m unittest discover -s tests
```

Report exact verification evidence and any untested surface. A passing checker proves document consistency only; it does not authorize implementation.
