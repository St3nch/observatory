# Observatory Codex Instructions

These instructions apply to the entire repository.

## Repository authority

- Treat the live repository as authority. Chat history, memory, uploaded copies, and sibling repositories are context only.
- Read the mandatory root sequence before nontrivial work:
  1. `README.md`
  2. `LLM_START_HERE.md`
  3. `ACTIVE_CONTEXT.md`
  4. `ROADMAP.md`
  5. `ROADMAP_RULES.md`
  6. `REPO_MAP.md`
  7. `00-project-overview.md`
  8. `01-harvest-register.md`
  9. `02-boundaries.md`
  10. `NEXT_SESSION_HANDOFF.md`
- For milestone or implementation work, follow the additional active read path in `NEXT_SESSION_HANDOFF.md`.
- If a required file is missing or current-state files disagree, stop. Report the conflict and do not guess.
- Run `python tools/check_authority_sync.py` before nontrivial mutation. A failing check blocks mutation.

## Required synchronization proof

Before proposing or making nontrivial changes, state:

- repository root;
- files read;
- last trusted completed milestone;
- active milestone or recovery gate;
- allowed work;
- forbidden work;
- missing files;
- contradictions;
- whether implementation is authorized.

Do not silently promote a draft, planning note, readiness review, or proposed owner phrase into authority.

## Core doctrine

- Observatory stores observations, not conclusions.
- The connected LLM interprets at read time.
- Accepted conclusions promote out to the owning consumer.
- Customer records and customer first-party data remain outside Observatory durable storage.
- Provider disagreement remains first-class evidence.
- Provider metrics remain provider-attributed testimony, not web truth.
- Rights and retention fail closed.
- LLMs receive no direct SQL, credentials, arbitrary queries, or table CRUD.
- Hammer tests are hard gates. Never inflate a proof class.
- Killed concepts stay killed. No VEDA Brain with a fake mustache.

## Change discipline

- Identify the active gate and edit class before changing files.
- Preserve unrelated user changes.
- Prefer updating an existing owning document over creating a competing source of truth.
- Planning-inbox material is not authority unless an accepted decision explicitly promotes it.
- A milestone name, future capability, available credential, running service, or existing tool does not create permission.
- For owner decisions, record the exact scope and explicit non-authorizations.
- When changing milestone state, update all current-state pointers and the authority-sync checker in the same batch.
- New folders require a clear repo-map placement and an index when project rules require one.

## Tool discipline

- Use Codex native local PowerShell, filesystem, Git, test, and review capabilities for ordinary development.
- Use the desktop app's built-in Git review and commit controls.
- Do not use old `ob-dev` Git tools.
- Use `ob-dev-mcp` only for its explicitly bounded project tools.
- Do not duplicate generic shell, Git, or arbitrary execution inside MCP.
- Never add or use PostgreSQL, migration, provider-spend, destructive, or production capabilities without a current accepted gate.
- Do not retry an identical failed mutation repeatedly. Read the resulting state first.

## Verification

For repository maintenance changes, run at minimum:

```powershell
python tools/check_authority_sync.py
python -m unittest discover -s tests
```

Use narrower tests during iteration, then the required suite before completion. Report exact commands, exit codes, failures, warnings, and untested surfaces.

## Handoff

Finish with:

- outcome;
- files changed;
- verification evidence;
- remaining uncertainty;
- current authority and non-authorizations;
- the next explicit owner gate, if one is required.
