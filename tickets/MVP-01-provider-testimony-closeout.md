# MVP-01 — Seven-surface provider-testimony closeout

**Status:** active  
**Kind:** read-only MVP milestone audit  
**Blocked by:** none; RANK-06 and routine F6 are closed  
**Approved by:** Project Steward  
**Start commit:** `d0452df370d746a32b3494e2317b47885465f007`  
**Implementation Writer:** none unless this audit earns a separate remediation ticket

## Why this ticket exists

The accepted DataForSEO roadmap requires a final empirical provider-testimony fidelity pass
before Observatory MVP closure. The question is not whether the individual tickets passed
their tests. The question is whether, across the complete accepted live provider bodies,
Observatory preserved and exposed the materially useful source-attributed testimony without
silently discarding, collapsing, relabeling, or overclaiming what the provider actually
returned.

This is a read-only closeout gate. A finding does not automatically authorize remediation,
another provider call, a new surface, Strategy work, or schema/API expansion.

## Surfaces in scope

The audit covers exactly these seven accepted live provider slices:

1. PF-03 — DataForSEO Google Keyword Overview;
2. PF-10 — DataForSEO Google Organic Live Advanced;
3. AI-03 / AI-06 — AI Optimization Search Mentions;
4. AI-09 / AI-12 — AI Optimization Target Metrics;
5. AI-14 / AI-17 — LLM Mentions Historical;
6. RK-02 / RK-05 — Google Related Keywords;
7. RANK-03 / RANK-06 — Google Ranked Keywords.

Related Keywords already received the deep full-body review that established this rubric.
Ranked Keywords received an equivalent full-body activation review. Their MVP-01 pass is a
consistency/reconciliation check against the final accepted parser/Recipe/API, not a demand to
invent new testimony or issue another request.

## Evidence prerequisite

Every surface begins from its exact accepted protected provider Evidence, not from provider
documentation and not from a repository fixture treated as authority.

The currently local protected roots for AI-09, AI-14, RK-02, and RANK-03 may be read in place
after fresh `status` and `scrub` checks. PF-03, PF-10, and AI-03 are older accepted roots that
are no longer present locally; restore their exact accepted encrypted Google Drive restic
snapshots into fresh local directories before review. For each restored root:

- require `format-2 ok` and clean scrub;
- independently reproduce the accepted Attempt/Capture inventory;
- inspect the exact accepted Capture body through the surface's verify-first inspect path;
- require the body byte count and SHA-256 recorded by the activation/closure authority;
- do not mutate the restored Evidence or treat the restore as a new Capture.

Repository Conformance fixtures may be compared to the verified bodies after Evidence identity
is established. They never substitute for Evidence authority.

## Per-surface review rubric

Read the complete exact provider body and trace the materially useful testimony through the
accepted strict parser, Recipe/Derivation, typed persistence, and current API surface. Check:

- requested subject versus provider-returned subject and every reconciliation boundary;
- fact, relationship, occurrence, and reference grain;
- provider-native identities and opaque vocabularies that must remain source-attributed;
- value states: stated values including zero, JSON null, absent, request-disabled,
  inapplicable/sentinel states, and malformed/unsupported shapes;
- Capture time, each independently stated Provider Update Time, and each Data Period;
- array/cardinality/order/duplicate behavior and whether order is testimony or non-semantic;
- corpus counts, returned counts, limits, prefixes, offsets, continuation/pagination testimony,
  and every bounded completeness/absence claim;
- exact URL/page/domain/source relationships without inventing canonical identity;
- provider classifications/aggregates versus Observatory-derived facts;
- unknown/additive fields and the accepted drift boundary;
- whether the API exposes the materially useful typed distinctions needed by an API-only
  consumer together with Recipe/provenance/completeness limits;
- one-Capture observations that must remain empirical testimony rather than invariants.

## Finding classes

Classify each material finding as one of:

1. **Preserved correctly** — provider distinction survives with correct provenance/limits.
2. **Known accepted limit** — testimony is deliberately untyped/unexposed or outside the
   accepted surface and is already represented honestly as such.
3. **Authority/documentation drift** — implementation is faithful but README/roadmap/ticket
   status language is stale or misleading; Steward-only documentation reconciliation may
   fix it.
4. **Material fidelity defect** — accepted parser/Recipe/persistence/API loses, collapses,
   fabricates, mislabels, or falsely completes materially useful provider testimony.
5. **Unproven branch** — the live Capture does not exercise a provider shape; record the
   inference limit. Use synthetic adversarial proof if needed under D12; do not call the
   provider merely to increase sample count.

A Class 4 finding blocks MVP closure and earns a separately bounded remediation ticket before
MVP-01 can close. Class 5 alone does not block closure when the accepted contract already
fails closed or truthfully exposes the limitation.

## Acceptance criteria

- [ ] Exact protected Evidence for all seven surfaces is identified and verified.
- [ ] PF-03, PF-10, and AI-03 old protected Evidence is restored fresh and verified against
      its accepted inventory/body hashes before use.
- [ ] All seven complete provider bodies are reviewed under the same fidelity rubric.
- [ ] Each surface has an explicit preservation/limit/finding summary grounded in Evidence
      and current accepted code/API behavior.
- [ ] Related Keywords and Ranked Keywords prior full-body findings are reconciled against
      their final accepted read APIs.
- [ ] No materially useful provider distinction is silently lost or falsely represented;
      otherwise the resulting remediation ticket is closed first.
- [ ] No one-Capture correlation or unobserved branch is promoted into a provider invariant.
- [ ] No Strategy score, recommendation, campaign meaning, canonical Page/domain identity,
      recurring acquisition state, or other downstream interpretation is introduced.
- [ ] No provider request, credential/account/pricing call, retry, continuation, pagination,
      Evidence mutation, spend, or push occurs under this ticket.
- [ ] Any secondary Strategy-consumer implications are handed off as non-authoritative notes,
      separate from Observatory fidelity findings.
- [ ] Roadmap/README status is reconciled to the final empirical result.

## Closeout decision

If all seven passes are accepted with no unresolved Class 4 finding, the Project Steward may
recommend Observatory MVP closure to [CHAZ]. Final MVP closure is a Product Owner + Steward
decision and must be recorded durably; MVP-01 itself does not predeclare that result.

## Working sequence

1. Recover and verify the three older off-host roots: PF-03, PF-10, AI-03.
2. Verify the four currently local roots: AI-09, AI-14, RK-02, RANK-03.
3. Review one surface at a time from exact body → parser → Recipe/Derivation → persistence →
   API, recording only material findings.
4. Reconcile any Class 3 documentation drift immediately when safe and bounded.
5. Stop and cut a remediation ticket for any Class 4 defect; do not opportunistically edit
   production code during the audit.
6. When all seven are green, perform final MVP closeout reconciliation and ask [CHAZ] for the
   Product closure decision.

## Legacy Evidence recovery proof — accepted 2026-09-01

[CHAZ] restored the exact accepted encrypted Google Drive restic snapshots for PF-03, PF-10,
and AI-03 into fresh `/tmp` directories. No provider call, Evidence mutation, backup deletion,
or repository mutation occurred during the restore/inspection procedure.

All three restored roots opened as `format-2 ok`, scrubbed without reported failure, and
independently reproduced the exact accepted committed Attempt/Capture IDs. The snapshotted
legacy inventory files independently contained the same IDs. PF-03's historical inventory
SHA-256 remained exactly
`58ac410ae1625c1088aceb32769d05e25b0474eecca083e075102512e1686d21`; AI-03's remained
`e2302f202834d01a0889aa57edfae36a223daaa9922b9763a6616f50dfc7e169`. PF-10's original
closure did not record an inventory digest, so MVP-01 does not invent one as historical
proof; its restored and snapshotted inventories were instead required to contain exactly the
accepted Attempt/Capture IDs. The restored PF-10 inventory file presently hashes to
`b47d3077fabf51d34656ad6726d6dd1b54626bc07c48996403cca9e04d89fb6f`, recorded here only as
an identity of the verified restored artifact, not as a retroactive activation-time claim.

Verify-first inspection of the restored accepted Captures reproduced the original provider
body identities exactly:

- PF-03 Keyword Overview — 26,270 bytes, SHA-256
  `d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c`;
- PF-10 Google Organic — 135,722 bytes, SHA-256
  `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`;
- AI-03 Search Mentions — 48,466 bytes, SHA-256
  `8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a`.

`MVP01_LEGACY_EVIDENCE_RECOVERY: PASS` is accepted. These restored bodies are now eligible as
the Evidence anchors for the corresponding MVP-01 fidelity passes. Repository Conformance
fixtures may be used for detailed read-only analysis only after byte identity with these
accepted body hashes is independently confirmed; the fixtures do not become Evidence
authority.

## Closure

<!-- Project Steward fills after all seven passes and any earned remediation are complete. -->
