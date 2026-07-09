# Claude Start Here — The Observatory

Status: historical / superseded
Authority: none
Superseded by: `LLM_START_HERE.md` (canonical read order) and `ACTIVE_CONTEXT.md` (current phase)
Archived: 2026-07-07 during the M7 audit-fix pass. The read order below is the pre-M0 original and is stale — do not follow it. Preserved for lineage only.

---

Read these files in order before reviewing or proposing changes:

1. `README.md`
2. `00-project-overview.md`
3. `01-harvest-register.md`
4. `planning-inbox/observatory-working-notes.md`
5. `planning-inbox/repo-first-research-triage.md`

Current posture:

- This is early planning, not implementation authorization.
- The Observatory is evidence-only.
- The connected LLM is the interpretation layer.
- The LLM must not get direct DB access.
- MCP tools should call an API; the API owns database access.
- Customer records stay out of Observatory.
- Customer-scoped SEO/GEO/SERP observations may enter later only under scoped, rights-labeled, provenance-complete rules.
- Strategy / recommendations / reports / agent actions belong outside Observatory.
- DataForSEO work should reuse Veda-era lessons, but fresh Observatory-native pulls happen later through controlled recipes.
- Do not propose schema or implementation until boundaries and CapturePackage planning are tighter.
