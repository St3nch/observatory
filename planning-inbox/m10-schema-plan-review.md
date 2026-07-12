# M10 Schema Plan Review — C2 Controlled Public Manual Observation Package

Status: planning review / closure-readiness note
Authority: none — advisory review only; roadmap and decisions remain authority
Milestone: M10 — Schema Planning Only
Date: 2026-07-10
Reviewer: ChatGPT / Observatory Steward

---

## Review Question

Does `planning-inbox/m10-logical-schema-plan-c2.md` satisfy the M10 requirement to plan schema for the accepted C2 first slice without crossing into migrations, implementation, provider work, customer data, API/MCP, dashboard work, or strategy/recommendation storage?

---

## Source Files Reviewed

- `ROADMAP.md`
- `ACTIVE_CONTEXT.md`
- `decisions/2026-07-10-m9-first-slice-closure.md`
- `planning-inbox/m9-first-slice-definition-proposal.md`
- `planning-inbox/m10-logical-schema-plan-c2.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- `contracts/README.md`
- M7 contract draft set by index coverage

---

## Review Result

```text
M10 logical schema planning is on the right track and appears safe enough for closure preparation, provided M10 records a few explicit defaults and preserves the no-migration/no-implementation boundary.
```

The logical schema plan stays inside the accepted C2 slice and does not appear to authorize physical DDL, migrations, provider pulls, customer data, API/MCP, dashboard work, or strategy/recommendation storage.

M10 still needs closure wording that records the final defaults below.

---

## Positive Findings

### 1. Slice containment holds

The plan stays centered on:

```text
Controlled Public Manual Observation Package
```

It does not broaden into:

- DataForSEO provider tasks;
- marketplace capture;
- customer overlays;
- SearchClarity reports;
- typed read API/MCP tools;
- recurring watch panels;
- dashboards;
- strategy/recommendation stores.

### 2. Logical responsibility level is preserved

The plan uses logical responsibilities and field concepts, not:

- DDL;
- migrations;
- SQL table definitions;
- indexes;
- constraints;
- ORM models;
- implementation code.

This fits M10's planning-only boundary.

### 3. Core evidence spine is represented

The plan covers the essential C2 spine:

```text
scope
observation package / envelope
observed artifact reference
raw support manifest if allowed
candidate observation
admitted observation
evidence identity
freshness / claim-use warning
audit event expectations
rejection reasons
```

This is enough for M11/M12 to understand what later implementation would need to prove.

### 4. Forbidden storage is explicitly rejected

The plan rejects schema ideas for:

- keyword recommendations;
- SEO/GEO strategy;
- provider winner logic;
- provider average truth score;
- customer order/identity/report state;
- private analytics;
- LLM reasoning transcripts as Observatory data;
- accepted business conclusions;
- agent task decisions.

This preserves the telescope/astronomer boundary.

---

## M10 Open Questions and Recommended Defaults

### Q1 — Should minimal query/panel context be included?

Recommended M10 default:

```text
Defer query/panel context from the base C2 schema plan unless M10 explicitly needs one non-strategy measurement-context placeholder.
```

Reason:

- C2 can prove the Observatory spine without query panels.
- Query panels add H14 complexity.
- Query panels are measurement programs, not strategy lists.
- Recurring watch/cadence concerns belong later.

M10 closure should say:

```text
H14 query panel immutability is deferred for the base C2 schema plan unless a minimal context placeholder is explicitly added without strategy, priority, recurrence, or provider execution semantics.
```

### Q2 — Should raw support be mandatory or optional?

Recommended M10 default:

```text
Raw support should be optional but first-class when included.
```

Reason:

- C2 should prove raw support behavior without assuming raw retention is always allowed.
- Rights and retention may require manifest-only or no-storage posture.
- Making raw support mandatory could force unsafe retention assumptions.
- Making raw support absent would weaken H12 planning.

M10 closure should say:

```text
The schema plan must support raw-support manifests and hash verification when raw support is allowed, but raw payload retention itself remains rights/retention-gated and may be blocked or manifest-only.
```

### Q3 — What evidence ID shape should M10 plan while OR-A4 remains open?

Recommended M10 default:

```text
Plan internal evidence identity only. Do not plan report-safe customer citation handles yet.
```

Reason:

- OR-A4 remains open for report-safe citation behavior.
- M15/M14 own customer/report/read-tool exposure.
- C2 only needs stable internal evidence identity for admitted observations.

M10 closure should say:

```text
M10 may plan internal evidence_id and internal citation_handle concepts only. Report-safe references, customer-facing handles, and external citation exposure remain deferred.
```

### Q4 — What is the minimum audit event set?

Recommended M10 default:

```text
Plan audit expectations for consequential transitions only, not a full operations ledger.
```

Minimum event types for M10 planning:

```text
package_rejected
package_validated
observation_admitted
observation_superseded
observation_withdrawn
raw_support_purged
```

Reason:

- M21-style operations do not exist; M19 owns full hardening.
- M12 needs enough audit shape to test consequential changes.
- Read-only access should not create audit events.
- Audit events must not store strategy or recommendations.

M10 closure should say:

```text
M10 plans only the minimum audit event concepts needed for later admission, rejection, supersession, withdrawal, and raw-support purge proof. Full operations hardening remains M19.
```

---

## Hammer Coverage Review

| Hammer | M10 coverage status | Notes |
|---|---|---|
| H1 Scope isolation | covered | Scope context required; customer/private identity blocked |
| H2 Rights fail-closed | covered | Rights class/basis required before admission |
| H3 Retention enforcement | covered | Retention class/basis and purge/no-storage behavior planned |
| H5 No strategy/recommendation storage | covered | Explicit anti-pattern list rejects strategy/recommendation storage |
| H6 Observation envelope validation | covered | Observation package responsibility exists; missing fields reject |
| H9 Freshness / claim-use warning | covered | Point-in-time warning concepts included |
| H12 Raw archive integrity | covered if raw support included | Needs closure default: optional but first-class when included |
| H15 Evidence ID / citation integrity | covered with caveat | Internal identity only; report-safe references deferred under OR-A4 |
| H18 Hostile weird input | partly covered | Plan includes rejection expectations; M11/M12 must make executable test plan |
| H19 Append-only observations | covered | Admitted observation mutation rejected; supersession path required |
| H21 Audit-first enforcement | covered at planning level | Minimum event concepts should be recorded at closure |
| H22 Rollback/recovery expectations | covered at planning level | M19 owns full proof; M10 must avoid designs that block restore/rollback |

---

## Deferred Hammer Review

The following remain correctly deferred for C2:

| Hammer | Deferred reason |
|---|---|
| H4 Customer-private rejection | positive path avoids customer data; rejection fixtures later |
| H7 Provider spend/duplicate tasks | no paid provider task |
| H8 Provider attribution/disagreement | no provider comparison |
| H10 AI/GEO overclaim | no AI answer surface evidence |
| H11 Marketplace evidence ceiling | no marketplace surface |
| H13 Provider drift/parser safety | no provider payload |
| H14 Query panel immutability | defer unless minimal context placeholder is explicitly needed |
| H16 Consumer request/overlay | no consumer workflow |
| H17 LLM/agent access | read tools are M14 |
| H20 Concurrency safety | later if write surface can race |

---

## Anti-Pattern Review

No unsafe storage pattern should be allowed into M10 closure.

M10 closure should explicitly keep these out:

```text
customer identity tables
customer order tables
SearchClarity report tables
strategy tables
recommendation tables
provider truth/winner tables
provider average score-as-truth tables
API/MCP access tables
scheduler/recurring capture tables
dashboard state tables
private analytics tables
cross-scope aggregate tables
```

---

## M11/M12 Handoff Readiness

The plan is strong enough to support a later M11/M12 handoff if M10 closure records:

- accepted logical responsibility groups;
- excluded schema families;
- applicable and deferred hammers;
- raw support optional/first-class default;
- internal-only evidence ID default;
- minimum audit event expectations;
- no migrations or implementation authorization.

M11 should later plan implementation foundation only after M10 closure.

M12 should later build and execute hammers only after M11.

---

## M10 Closure Recommendation

```text
Recommend closing M10 after recording the four defaults above and updating roadmap/context/handoff to M11.
```

M10 closure should not accept a physical schema.

M10 closure should accept only a logical planning target for M11/M12.

---

## Anti-Drift Notes

Do not infer from this review that:

- migrations are authorized;
- implementation is authorized;
- physical schema is final;
- Postgres changes are authorized;
- M11 has started;
- M12 has started;
- hammers have passed;
- raw payload retention is always allowed;
- report-safe citations are planned;
- query panels are included by default;
- manual capture is production-approved.

---

## Final Rule

```text
M10 may close on logical schema responsibility planning.
M10 may not become build work.
```
