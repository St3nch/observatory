# The Observatory — LLM Start Here

Status: draft 1  
Date: 2026-07-07  
Purpose: first file every LLM should read before working in this repo.

---

## 1. Stop and Read This First

You are working in **The Observatory** repo.

Do not treat this as:

- a generic SEO tool;
- a dashboard project;
- a strategy engine;
- a customer CRM;
- a random database experiment;
- a Kaizen replacement;
- a Neon Ronin subsystem;
- a SearchClarity customer database;
- a place to freestyle schema from vibes.

The Observatory is an evidence-only, LLM-first project for external SEO/GEO/SERP visibility observations and typed read tools.

Core rule:

```text
The Observatory stores what was observed.
The connected LLM interprets at read time.
Accepted conclusions promote out to the owning consumer.
```

---

## 2. Required Root Reading Order

Before doing any project work, read:

```text
README.md
ACTIVE_CONTEXT.md
ROADMAP.md
ROADMAP_RULES.md
REPO_MAP.md
00-project-overview.md
01-harvest-register.md
02-boundaries.md
NEXT_SESSION_HANDOFF.md
```

Then read the active milestone's required reading from `ROADMAP.md`.

If a milestone lists a folder as required reading, that folder must have a `README.md`. Read the folder README first.

---

## 3. Current Hard Boundaries

These are not suggestions.

- The Observatory stores observations, not strategy.
- No stored recommendations, scores-as-truth, business decisions, plans, or strategy records.
- No customer records.
- No customer first-party analytics in Observatory.
- Customer first-party data may only appear through read-time overlay contracts unless a future explicit owner ruling says otherwise.
- Owner-internal first-party performance may be considered only under internal scope and explicit boundary rules.
- LLMs and agents never receive SQL or direct credentials.
- Typed API/MCP read tools are the only door.
- Provider data is observed testimony, not truth.
- Provider disagreement is preserved.
- Rights and retention must fail closed.
- Hammer tests are a hard gate for schema/API/tool/provider/capture behavior.
- Killed concepts stay killed.

---

## 4. Current Project Voice

The stewardship stance is:

```text
not yet — earn it
```

That means:

- do not create tables before contracts/research justify them;
- do not create folders without a reason;
- do not promote working notes into authority;
- do not turn future ideas into active implementation;
- do not mistake ambition for approval.

Be useful, but stay fenced.

---

## 5. What To Do Before Any Work

Before planning, editing, or implementing, summarize:

1. what files you read;
2. what the active milestone is;
3. what boundaries affect the work;
4. what you are not allowed to change;
5. what blocker or next action you are addressing.

If you cannot answer those five things, you are not ready to work.

---

## 6. Where Things Go

Use `REPO_MAP.md`.

Quick version:

| Need | Location |
|---|---|
| project overview | root docs |
| roadmap and active state | root docs |
| boundary law | `02-boundaries.md` and future `docs/boundaries/` |
| rough notes | `planning-inbox/` |
| research outputs | `research/` |
| contracts | `contracts/` |
| schema planning | `schema/` |
| hammer tests | `testing/` |
| proof workflows | `proofs/` |
| project-law decisions | `decisions/` once earned |
| old/superseded docs | `archive/` |

Do not create random locations because they sound neat.

---

## 7. If You Are Asked To Implement

Implementation includes schema, migrations, provider calls, paid capture, APIs, MCP tools, persistence behavior, or customer-facing output behavior.

Before implementation:

1. read the milestone required reading;
2. verify gates in `ROADMAP.md`;
3. verify rights/retention status;
4. verify hammer-test expectations;
5. verify owner approval where required.

If any of those are missing, stop at planning.

---

## 8. What To Avoid

Do not:

- invent a Strategy Layer store;
- create an opportunity/recommendation table;
- create a customer table;
- put GA/customer private data into Observatory;
- average providers into fake truth;
- create an MCP tool that hides uncertainty;
- create a dashboard side quest;
- skip roadmap required reading;
- silently change roadmap scope;
- bury important context in chat only.

---

## 9. Useful Mental Model

```text
The Observatory is the telescope.
The connected LLM is the astronomer.
Kaizen / Neon Ronin / SearchClarity own accepted action, reports, decisions, or operations.
```

If the telescope starts writing business plans, something went wrong.

---

## Final Rule

```text
Read the map. Read the roadmap. Read the boundaries. Then work.
```
