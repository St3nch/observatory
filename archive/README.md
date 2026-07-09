# Archive

Status: archive index
Authority: folder index; archived files keep their own labels and history
Purpose: preserve superseded, historical, or model-specific material without confusing it for current authority

---

## Purpose

`archive/` exists to preserve useful historical material after it is no longer part of the active read path.

Archiving is not deletion. Archiving is also not approval.

---

## What Belongs Here

- superseded onboarding files
- historical handoffs
- model-specific notes no longer used as active context
- old planning drafts retained for lineage
- superseded decision records when a successor is clearly linked

---

## What Does Not Belong Here

- credentials or secrets
- customer private data
- customer first-party analytics
- raw provider payloads
- active authority docs
- implementation code
- files moved just to hide unresolved conflicts

---

## Reading Order

There is no default reading order for archived files.

Read archived files only when current authority docs, handoffs, or roadmap milestones explicitly point here.

---

## File Index

| File | Status | Purpose | Notes |
|---|---|---|---|
| `CLAUDE_START_HERE.md` | historical / superseded | Pre-M0 Claude-specific onboarding note with the original (now stale) read order | Superseded by `LLM_START_HERE.md`; moved here 2026-07-07 (M7 audit-fix pass, ISS-06) |

---

## Related Roadmap Milestones

- M2 — creates archive folder and archive rules
- M3 — may preserve historical/model-specific docs after adding classified knowledge docs
- M4 — may archive superseded boundary drafts after reconciliation

---

## Notes for LLMs

Do not treat archived files as current authority unless a root authority file explicitly says to.

Do not delete archived files unless the owner explicitly approves deletion.

When moving a file here, preserve its filename or add a clear historical date/context label.

If an archived file conflicts with a root authority file, root authority wins unless a later accepted decision says otherwise.

---

## Last Review Notes

```text
Last reviewed: 2026-07-07
Reviewer: Claude (Observatory Project Steward role), M7 audit-fix pass
Result: First archive move completed (CLAUDE_START_HERE.md); open issue resolved
Open issues: Owner must manually delete the tombstone at planning-inbox/CLAUDE_START_HERE.md (steward tools cannot delete files)
```
