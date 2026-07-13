# Repository Tools

Status: maintenance
Authority: none
Purpose: hold deterministic repository-maintenance checks that support, but do not replace, Observatory authority documents

## Contents

- `check_authority_sync.py` — verifies that current-state files agree on the active milestone, required recovery markers exist, suspended decisions remain visibly suspended, and machine-readable project status matches the authority documents.

## Rules

- Tools report repository state; they do not create project authority.
- A passing check does not authorize implementation.
- Update the checker in the same accepted batch that legitimately changes milestone state.
- Keep this folder free of provider execution, database execution, arbitrary shell wrappers, secrets, and customer data.
