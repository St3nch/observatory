# M13 DataForSEO SERP Usage Workbook Baseline — 2026-07-12

Status: owner-uploaded provider-usage baseline evidence
Authority: evidence only; not provider execution authority
Milestone: M13 — Provider Admission and Controlled Pull Plan
Source file name: `serp-usage.xlsx`
Source file SHA-256: `8a394460940aba7550610ceb5f816982f263d2b7955be2e866a2e998fbed9cc0`
Source file bytes: `6800`
Reviewed: 2026-07-12

---

## Workbook Inspection

Workbook contains one worksheet:

```text
Main
```

Detected header row:

```text
ID
Search Engine
Keyword
Location Code
Language Code
Task set
Task complete
Turnaround time
Cost
IP
```

Populated provider usage rows:

```text
0
```

Baseline disposition:

```text
The workbook is empty before the M13 live campaign.
Any populated row in the next uploaded version is a candidate new provider-usage event.
```

---

## Privacy Posture

The workbook may later contain IP addresses and account-specific task metadata.

Therefore:

- the uploaded workbook remains outside the Git repo;
- the public repo records only the workbook hash, row counts, sanitized match results, and cost summaries;
- raw IP values must not be committed;
- future versions are read-only witnesses unless the owner explicitly asks for a modified copy.

---

## First Delta Gate

After campaign recipe C00 executes, the next workbook upload should be checked for:

```text
exactly one new populated row
usage ID matching provider task ID where possible
Google search engine context
keyword: observatory test page
location_code: 2840
language_code: en
task timestamps consistent with local manifest
usage cost matching top-level and task-level response cost
IP presence recorded only as true/false in repo-safe evidence
```

Any extra, missing, duplicate, changed, or ambiguous row blocks promotion of C01 until reviewed.

---

## Final Rule

```text
This empty workbook is the clean before-image.
Later uploads become provider-account witnesses against this hash and row-zero baseline.
```
