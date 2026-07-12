# M18 Watch Panel Policy v0.1

Status: planning proposal
Milestone: M18
Date: 2026-07-12

## Purpose

Define the smallest responsible recurring-watch policy without implementing or authorizing recurrence.

## Watch-panel eligibility

A candidate watch panel is eligible for review only when all are true:

- one declared Observatory scope;
- one immutable query-panel version;
- measurement-only purpose;
- admitted public source family;
- rights and retention classified;
- provider/capture instrument separately admitted;
- exact recipe and request shape frozen;
- cost known or bounded;
- duplicate-prevention key defined;
- stop conditions defined;
- no customer/private data;
- no strategy, recommendation, or report state.

Unknown or mixed scope, source, rights, retention, recipe, or cost blocks eligibility.

## Cadence classes

Cadence is a maximum frequency, not permission to run.

```text
manual_only
monthly_review_candidate
biweekly_review_candidate
weekly_review_candidate
```

No daily, hourly, event-driven, or continuous class is admitted in M18.

Cadence selection must be based on observed volatility, freshness requirements, claim use, provider cost, and review capacity. Convenience or anxiety is not a cadence justification.

## Budget policy

Every future recurring proposal must declare:

- maximum cost per run;
- maximum runs per rolling 30 days;
- maximum rolling 30-day spend;
- retry ceiling;
- polling ceiling;
- zero automatic budget increases;
- owner approval required for any ceiling change.

A missing or exceeded ceiling blocks execution.

## Duplicate prevention

The future duplicate key must bind at minimum:

```text
scope_id
query_panel_version_id
recipe_id
provider_or_capture_instrument
scheduled_window
request_shape_hash
```

A matching successful, running, approved, or unresolved attempt blocks another attempt in the same window. Failures do not automatically authorize retries.

## Stop conditions

A future watch panel must stop before capture when any of these occurs:

- rights or retention becomes unknown or invalid;
- provider terms or endpoint behavior changes materially;
- cost exceeds a declared ceiling;
- duplicate key collides;
- panel version is not active or is ambiguous;
- source family is no longer admitted;
- credentials or account limits are unresolved;
- request shape drifts;
- failure budget is exhausted;
- output drift or raw-shape drift exceeds the accepted recipe boundary;
- owner disables the panel.

## Failure budget

Proposed maximum for any future candidate:

```text
one failed attempt per review window
zero automatic retries unless separately approved
zero silent fallback providers
zero silent request-shape changes
```

## Manual review gates

Review is required:

- before first run;
- after first successful run;
- after any failure;
- after any provider, price, rights, retention, endpoint, or shape change;
- before cadence increase;
- before budget increase;
- before adding or removing panel items;
- before enabling a new source family.

## Warning requirements

Read outputs from future watch panels must disclose:

- last successful observation time;
- current freshness/staleness state;
- missed or blocked windows;
- incomplete panel coverage;
- source/provider limitations;
- non-synchronous comparison warnings;
- panel version and recipe identity;
- that absence is bounded to the observed panel/run context.

## Explicit non-authorizations

This policy does not authorize:

```text
scheduler code
cron or task creation
provider calls
recurring capture
autonomous spend
credentials
broad crawling or scraping
customer data
Postgres or migrations
production API/MCP
reports or recommendations
```
