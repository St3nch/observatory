# Decision — Accept M18 Watch-Panel Policy, Reject v1 Recurring Execution, Activate M19

Status: accepted decision
Date: 2026-07-12
Milestone transition: M18 -> M19

## Decision

The owner accepts the M18 recurring watch-panel policy as future planning guidance and rejects recurring capture execution for Observatory v1.

Accepted M18 rulings:

- admitted planning cadence classes are `manual_only`, `monthly_review_candidate`, `biweekly_review_candidate`, and `weekly_review_candidate`;
- weekly is the highest admitted planning cadence class;
- daily, hourly, continuous, event-driven, and adaptive recurrence remain blocked;
- every future recurring proposal requires explicit per-run and rolling 30-day budget ceilings;
- no automatic budget increases, retries, fallback providers, or request-shape changes are allowed;
- deterministic duplicate prevention must bind scope, immutable panel version, recipe, provider/instrument, scheduled window, and request-shape hash;
- unresolved duplicate collisions block execution;
- rights, retention, provider, pricing, endpoint, request-shape, credential, account-limit, panel-version, failure-budget, and owner-disable changes stop a future panel before capture;
- manual review is mandatory before first execution, after first success, after every failure or material drift, and before cadence, budget, membership, or source-family changes;
- M18 creates no scheduler code, cron definition, Windows task, automation file, queue worker, recurring job record, credential path, or provider execution task.

## M18 closure

M18 is complete because recurring capture can now be approved or rejected responsibly. The accepted outcome for v1 is rejection of execution while preserving a bounded future policy.

## M19 activation

M19 — Hardening, Backup, Recovery, and Operations is active for planning only.

Allowed M19 planning includes:

- backup posture;
- restore-proof design;
- audit-log expectations;
- secret-exposure checks;
- retention-cleanup proof;
- operational runbooks;
- operational-risk documentation.

## Explicit non-authorizations

This decision does not authorize:

```text
scheduler implementation
recurring capture execution
provider calls or autonomous spend
credentials or secret delivery
broad crawling or scraping
Postgres creation
physical schema or migrations
production API/MCP
customer data or reports
strategy or recommendation storage
production deployment or integration
```

## Authority

This decision closes M18 and activates M19 planning. It does not activate M20 or authorize M19 implementation beyond separately bounded and approved work.
