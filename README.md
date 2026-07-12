# The Observatory

The Observatory is a standalone planning project for an evidence-only SEO/GEO/SERP visibility database and LLM-readable evidence layer.

It stores observations, not strategy.

The connected LLM interprets at read time; the database does not store strategy, recommendations, or scores-as-truth.

Current phase authority lives only in `ACTIVE_CONTEXT.md`. Do not restate a milestone here. The post-v1 database sequence lives in `POST_V1_DATABASE_ROADMAP.md`, but that roadmap does not authorize Postgres, DDL, migrations, ingestion, production, customer data, reports, or strategy/recommendation storage unless the active context and an explicit owner decision open the exact gate.

## Start here

`LLM_START_HERE.md` owns the canonical read order. Every fresh human or LLM session must read the LLM-first path before recommending work or making edits:

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

Planning inbox material is indexed in `planning-inbox/README.md` and is not authority unless promoted by an explicit roadmap/doctrine change.

Ancestor/sibling repos may provide optional historical context, but this repo's live committed authority wins for Observatory work.
