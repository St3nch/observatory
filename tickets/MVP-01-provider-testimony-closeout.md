# MVP-01 — Seven-surface provider-testimony closeout

**Status:** blocked — Google Organic material-fidelity remediation required  
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

## Seven-surface Evidence/fixture identity gate — accepted 2026-09-01

After the legacy restore proof above, [CHAZ] independently compared each verify-first inspected
provider body to its repository Conformance fixture. The three restored legacy bodies were
byte-identical to their fixtures. The four currently local protected Evidence roots first
opened as `format-2 ok` and scrubbed without reported failure; their exact accepted Captures
were then inspected and compared byte-for-byte to their fixtures.

All seven comparisons passed:

- PF-03 Keyword Overview — 26,270 bytes, SHA-256
  `d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c`;
- PF-10 Google Organic — 135,722 bytes, SHA-256
  `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`;
- AI-03 Search Mentions — 48,466 bytes, SHA-256
  `8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a`;
- AI-09 Target Metrics — 1,775 bytes, SHA-256
  `7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2`;
- AI-14 Historical LLM Mentions — 5,246 bytes, SHA-256
  `4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781`;
- RK-02 Related Keywords — 177,120 bytes, SHA-256
  `e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb`;
- RANK-03 Ranked Keywords — 390,955 bytes, SHA-256
  `5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84`.

`MVP01_ALL_7_EVIDENCE_FIXTURES: PASS` is accepted. This establishes that detailed semantic
review may read the repository Conformance fixtures as exact copies of the already-verified
provider bodies while Evidence remains the authority. It does not make fixtures authority,
authorize provider transport, or prove that Observatory's interpretation of those bytes is
correct; the per-surface fidelity passes below must still trace body → parser → Recipe /
Derivation → typed persistence → API.

## Seven-surface semantic fidelity review — 2026-09-01

The Project Steward reviewed the exact Evidence-identical fixture bodies against the accepted
strict parsers, Recipe/Derivation contracts, typed persistence, and current read APIs at exact
repository commit `7946433600b93815c5f7a1976cbf8ba7c66fa5b2`. The fixture/body hashes above
anchor the reviewed provider bytes; Git anchors the exact implementation. The review does not
use LLM recollection as artifact identity.

### PF-03 — Keyword Overview

**Verdict:** Class 1 preserved correctly, with Class 2 / Class 5 bounded limits; no Class 4.

The accepted extended Recipe carries exact requested/returned keyword reconciliation, coverage,
current metrics, 441 nonuniform monthly Data-Period facts, provider trend testimony, keyword
properties, average-backlink testimony, search intent, exact decimal semantics, field states,
and the independently stated metrics/backlink/intent clocks. The real stated zero monthly point
survives as zero. Request-disabled SERP/clickstream enrichment remains distinguishable from
absence. Populated SERP/clickstream/Bing-normalized branches are unobserved or outside the
accepted Recipe rather than guessed. The duplicated returned location/language echo agrees with
the verified Attempt in PF-03; the accepted metrics contract deliberately serves the verified
request context rather than inventing a second measurement-context identity from that agreeing
echo.

### PF-10 — Google Organic

**Verdict:** Class 1 for the accepted six-kind Recipe, plus **Class 4 material fidelity defect**
for provider testimony that is present in the exact body but unavailable to an API-only
consumer.

The accepted path correctly preserves 111 top-level SERP placements, 97 distinct organic
placements, both rank systems, page/position, exact URLs without canonical Page identity, one
AI Overview presence fact, 15 semantic AI Overview source relationships with all 18 source
occurrences, four PAA question relationships with occurrence testimony, nine exact related
queries, provider result time, result/corpus counts, and request context. Duplicate exact URLs
at different placements remain separate facts; AIO top-level versus element source loci remain
distinct.

The exact PF-10 body also contains materially useful search-visibility testimony that PF-11
explicitly left raw to keep the first Recipe bounded: a Top Stories block with child results
carrying source/domain/title/URL/timestamp, a Video block with child results carrying
source/title/URL/timestamp, organic-result publication timestamps on returned ranked results,
and sitelink relationships under an organic result. The current parser/Recipe/API reduces the
Top Stories and Video blocks to feature placement/presence and does not type or expose those
child result relationships; it also omits the observed organic publication time and sitelink
relationships. These are not speculative provider fields: they occur in the Evidence-identical
PF-10 body. They are historically irrecoverable query → SERP result → URL / freshness
relationships useful to downstream search-visibility reasoning, so raw-Evidence retention alone
does not satisfy the MVP consumer-fidelity gate. This is one bounded Google Organic
under-modeling defect, not a requirement to type every decorative/null provider field.

Full AI Overview prose/markdown and PAA expansion content remain a separate Class 2 retention /
redistribution boundary; rating, price, alternate right-rail behavior, populated related-result
families, and other unobserved branches remain Class 5 rather than reasons for another provider
call.

### AI-03 — Search Mentions

**Verdict:** Class 1 preserved correctly; no Class 4.

The API preserves the five returned question/answer facts, exact Markdown answers, current AI
search volume, web-search flag, first/last provider response clocks, sixty monthly Data-Period
facts, forty-eight structured source facts with exact source metadata and per-item rank
occurrences, and the explicit 5-of-3055 prefix context including offset and opaque continuation
token. Current volume is not collapsed into the newest monthly point. The live-null
`search_results`, `brand_entities`, and `fan_out_queries` families remain explicit null states;
non-null shapes are Class 5 unproven branches.

### AI-09 — Target Metrics

**Verdict:** Class 1 for admitted-history testimony plus Class 2 known API limits; no Class 4.

The accepted history exposes total mentions/search volume, all ten exact source-domain facts,
provider lexical array positions without calling them rank, singleton location/language/platform
groupings, explicit empty optional grouping families, result topology, request context, and the
internal-list-limit completeness warning. No Provider Update Time or Data Period is invented.
Measurement Outcomes and Holdings remain separately gated and are an explicit product/API
limit, not hidden semantic loss in the admitted-history document.

### AI-14 — Historical LLM Mentions

**Verdict:** Class 1 preserved correctly; no Class 4.

All twelve returned month facts preserve exact year/month Data Period, mentions, and AI search
volume. The exact requested date window is served separately from the returned facts;
unreturned requested periods are represented as unreturned periods rather than synthesized zero
Observations; admitted-empty history remains distinct from failure/no-history. Capture time is
not substituted for Data Period or a nonexistent Provider Update Time.

### RK-02 — Related Keywords

**Verdict:** Class 1 preserved correctly with already accepted bounded limits; no Class 4.

The prior full-body review and final RK-05 contract remain aligned: seed versus returned-item
loci stay distinct; current versus monthly demand stays distinct; the provider's multiple
structure-local clocks remain independent; field states, exact decimal/array testimony,
keyword properties/backlinks/intent/SERP detail, semantic relationships, and every provider
relationship occurrence remain typed. Frontier relationship targets do not falsely require a
returned keyword-data node. Provider `total_count`, `items_count`, derived returned-item count,
and relationship-occurrence count remain separate grains. No tree/BFS/relevance/canonical
keyword meaning is invented.

### RANK-03 — Ranked Keywords

**Verdict:** Class 1 for the accepted history document plus Class 2 known limits; no Class 4.

The final RANK-06 read contract remains aligned with the prior full-body review: the provider's
100-of-248 returned prefix is explicit; corpus aggregates remain separate from returned rows;
the two provider rank systems remain unreconciled; exact placement URLs are content rather than
canonical Page identity; Ranked-local keyword facts and monthly Data Period facts remain
surface-local; provider item/monthly occurrence bridges preserve returned-array testimony; and
all four time pillars remain distinct. Accepted Product Option 1 keeps certain provider SERP
prose values Evidence-only while preserving their states. Ranked Measurement Outcomes and
Holdings remain explicitly unimplemented, so empty Ranked history cannot be interpreted as
unranked/never-measured; the API documents that limitation directly.

### Closeout finding summary

- Class 4 blockers: **one**, the bounded PF-10 Google Organic under-modeling described above.
- Class 3 drift: `README.md` still describes the pre-AI-14 Historical checkpoint and omits the
  completed Historical, Related Keywords, Ranked Keywords, and routine F6 state. Final README
  reconciliation waits until the Class 4 remediation is accepted so it can describe one stable
  MVP candidate rather than another transient checkpoint.
- No review finding authorizes another provider request. The PF-10 exact protected body is
  sufficient to design and prove the remediation with zero provider/network activity.

MVP-01 therefore remains blocked. The Google Organic defect earns one separately bounded
remediation ticket; production/parser/Recipe/schema/API code must not be opportunistically
changed inside this audit ticket. After that remediation closes, MVP-01 must re-check the
Google Organic consumer document, reconcile README/roadmap status, and only then may the
Steward recommend final Observatory MVP closure to [CHAZ].

## Closure

<!-- Project Steward fills after the Google Organic remediation and final reconciliation. -->
