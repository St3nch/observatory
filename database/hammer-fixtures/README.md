# Broken hammer fixtures

These are intentionally hostile DB-4 migration candidates. They may never enter accepted migration history.

Every fixture must declare the closed metadata required by the R3 authority:

```text
fixture_id
violated_invariant
rejection_class
rejection_point
expected_sqlstate
residue_relation
history_expectation
cleanup_expectation
```

Rejection classes:

- `postgresql_native` — PostgreSQL itself rejects the candidate with the declared SQLSTATE.
- `runner_detected` — PostgreSQL permits the dangerous DDL, so a bounded semantic detector must reject it before history insertion.

File presence and static validation are not execution proof. The current frozen `ob-dev` executor is SHA-bound to the original eight check IDs; the eight additional R3 fixtures remain complete but not runnable until a later authorized compatibility decision and live disposable campaign.
