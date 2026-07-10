# Public Page Snapshot and Archival Evidence Research Report for The Observatory

## Executive Summary

A **public page snapshot** is best treated as a **time-bound observation** of a public-facing surface captured under a defined context: URL, time, tool, browser/device, viewport, locale, account state, and any other condition that could change what was shown. It is not permanent proof of what every user saw, nor proof of the page’s full underlying state everywhere and always. Google’s own documentation is blunt that crawling and indexing behavior is context-dependent, robots instructions are limited, and dynamic rendering can materially affect what gets captured; the Internet Archive likewise warns that archived pages are often incomplete, JavaScript-heavy pages are harder to preserve, and some archived links can fall back to live-web resources. citeturn21view0turn23view0turn20view2turn35view0

The safest default for Observatory-style evidence is usually **a bounded visual artifact plus provenance metadata plus integrity hash**, not “store the whole internet and hope legal catches up later.” In practice, that means screenshots, basic extracted fields, headers/status where lawfully obtainable, and a rights/retention classification. Full raw HTML copies, rendered DOM dumps, or bulk copies of platform pages carry meaningfully higher copyright, terms, privacy, and evidentiary ambiguity than a screenshot or a licensed API payload. Public visibility is not blanket permission for unrestricted storage, redistribution, or automation. That is not a philosophical quibble; it is written directly into many platform terms and API policies. citeturn13view0turn13view5turn25search3turn25search7turn12view7turn37view0turn24view0

If The Observatory is supposed to be the telescope and not the astronomer, the preservation layer should record **what was observed**, **how it was observed**, **what rights caveats attach to it**, and **how much confidence the artifact supports**. Hashes help prove that a stored artifact has not changed since hashing, but they do not prove lawful capture, authenticity of source, or representative truth of the page in all contexts. NIST’s hash guidance supports the integrity piece; chain-of-custody guidance from NIJ supports the provenance piece; neither turns a dubious capture into holy scripture. citeturn11search17turn11search10turn34view3

The strongest decision-ready conclusion is this: **The Observatory should usually prefer one of four evidence patterns** depending on source and rights posture:  
**screen-only**, **screen + normalized metadata**, **licensed API payload + hash**, or **reference-only to a trusted third-party archive**. Full-page copy retention should be the exception class, not the default class. Marketplace reviews/comments, user-generated content, faces, usernames, and public-but-sensitive data should stay on a very short leash. citeturn20view1turn19view0turn28view0turn37view0turn34view0

## Confidence and Source Quality

### Confidence and Source Quality

**High confidence** applies to official facts about robots controls, Google Search controls, Wayback/Perma capabilities, DataForSEO endpoints, and official platform/API restrictions because those come from standards bodies, platform documentation, and published terms. citeturn21view3turn21view0turn23view0turn20view1turn19view0turn31view1turn31view3turn24view0

**Medium confidence** applies to technical comparisons among screenshot, HTML, text extraction, raw HTTP capture, and hash workflows. Those comparisons are supportable from official tool docs and preservation guidance, but some conclusions are still technical inference because the law does not supply a neat evidence-score API. citeturn35view0turn35view1turn35view2turn34view7turn34view6

**Lower confidence** applies where the answer turns on legal interpretation across jurisdictions, mixed copyright/fair-use questions, platform enforcement posture, or unclear distinctions between manual observation and semi-automated browsing. For those items, the right answer is often: **Unclear — needs legal/terms confirmation.** The U.S. Copyright Office itself emphasizes that fair use is fact-specific and not a substitute for legal advice. citeturn36view1turn36view2

### Source List

All web sources below were accessed on **July 10, 2026**.

**Primary and official sources used most heavily:** RFC 9309 Robots Exclusion Protocol; Google Search Central documentation on robots.txt, robots meta controls, structured data, and AI features; Internet Archive Wayback Machine help and APIs; Perma.cc developer documentation; DataForSEO SERP and OnPage documentation; Google Maps Platform terms; Google Business Profile APIs; YouTube Terms and Developer Policies; Etsy Terms of Use and API Terms; Pinterest Terms and Developer Guidelines; Reddit User Agreement, Public Content Policy, and Data API Terms; Shopify Terms and Storefront API docs; Microsoft/Bing official docs on API retirement and Webmaster tooling; NIST hash guidance and privacy framework; NIJ chain-of-custody guidance; FTC COPPA materials; U.S. Copyright Office materials on copyright and fair use. citeturn21view3turn21view0turn21view1turn23view0turn20view1turn20view2turn19view0turn31view1turn31view2turn31view3turn12view7turn28view0turn13view5turn24view0turn13view0turn12view6turn25search0turn25search7turn12view3turn37view0turn38view4turn12view4turn27search0turn17search5turn17search12turn11search17turn34view1turn34view3turn34view2turn36view1turn36view3

**Reputable third-party sources used carefully and labeled as such:** ABA discussion of screenshot admissibility risks; Library of Congress discussion of legal issues in web archiving; NDSA Levels of Digital Preservation; Ars Technica reporting on the archive.today trust incident. These support practice guidance and context, not binding law. citeturn34view5turn36view0turn34view6turn33search0

### Official Facts, Third-Party Claims, Interpretation, and Inference

| Category | What belongs here | How this report treats it |
| --- | --- | --- |
| Official facts | Standards, official docs, terms, API docs, help docs | Treated as the primary source of truth. citeturn21view3turn21view0turn20view1turn19view0turn24view0 |
| Third-party claims | Preservation practice, evidentiary commentary, archive.today concerns | Used only where official sources are absent or not enough, and labeled accordingly. citeturn34view5turn36view0turn33search0 |
| Legal/terms interpretation | Whether a capture is likely low/medium/high risk | Presented as research-informed risk categorization, **not legal advice**. Supported with source text where possible. citeturn36view1turn36view2turn13view0turn13view5 |
| Technical inference | Whether a method is more or less reproducible, tamper-prone, report-friendly | Called out as inference from tool behavior and preservation design. citeturn35view0turn35view1turn34view7turn34view6 |
| Unclear items | Jurisdictional legal edge cases, manual-vs-automation gray zones, redistribution scope on some platforms | Marked: **Unclear — needs legal/terms confirmation.** citeturn36view1turn36view2turn12view0turn12view4 |

## Research Findings

### Public Page Snapshot Concept

A public page snapshot is an **observation of a public surface at a particular time and under a particular capture context**. That context matters because web pages vary by device, viewport, location, language, login state, cookies, personalization, feature flags, JavaScript timing, and even whether a crawler versus a human browser loaded the page. Google explicitly documents that AI/Search inclusion and crawler access depend on crawlability, index eligibility, snippet controls, and other conditions; Playwright and DataForSEO likewise expose that screenshot output is contingent on browser settings, full-page versus viewport mode, and device/browser presets. citeturn23view0turn35view0turn31view1turn31view3

**Required principle:** a page snapshot is an observation of a public surface at a specific time and capture context, not permanent proof of universal content state. That principle is consistent with how the Internet Archive describes the incompleteness of archived pages, how it treats JavaScript and missing resources, and how search platforms document crawl/index controls. citeturn20view2turn21view0turn23view0

The difference between **observing a page** and **copying a page** is not semantic fluff. Observation can be limited to noting what was displayed at time T in context C; copying can involve reproduction, storage, redistribution, transformation, or automation rights that are separately constrained by copyright, contract, robots, and privacy law. The U.S. Copyright Office explains that copyright applies automatically to original works, that fair use is context-specific, and that quotes or limited portions may be permissible in some circumstances but not by fixed rule. citeturn36view3turn36view1turn36view2

What a snapshot **can prove**: that a capture process produced artifact A, under documented conditions, showing content X at URL U at time T. What it **cannot prove** on its own: that every user saw the same thing; that the page “always” displayed that content; that the content was lawfully reused; that the source was authentic in a legal sense; or that the artifact was complete. NIJ chain-of-custody guidance and ABA evidentiary commentary both reinforce that provenance and tamper handling matter, while screenshot evidence can be challenged for incompleteness or alteration. citeturn34view3turn34view5

A usable minimum metadata set for time-bounded page evidence is: capture timestamp with timezone, URL and canonical URL if known, capture operator/tool, browser/device/viewport, status/headers where available, locale/language, login/account state, and method-specific hashes. Without that, the artifact is still a picture, but it is a worse piece of evidence. citeturn34view3turn35view0turn35view1

### Capture Methods

The table below compares the main capture methods the user requested. “Risk” below is a research-informed operational risk label, not a legal ruling.

| Method | What it captures | What it misses | Evidence strength | Storage burden | Legal / terms risk | Technical risk | Best use | Bad use |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| Manual screenshot | Visible viewport only | Off-screen content, hidden text, headers, code | Medium for “what was seen” | Low | Usually lower than bulk copying, but redistribution still risky if copyrighted/UGC-heavy. citeturn35view0turn36view2 | Can omit context; easy to crop misleadingly. citeturn34view5 | Human-observed proof of display state | Claiming full-page completeness |
| Browser screenshot automation | Visible viewport under controlled browser | Same as above unless full-page | Medium | Low | Higher than manual if platform forbids automated access. citeturn13view5turn13view0turn25search7 | Timing/personalization variance | Repeatable QA-style captures | Silent recurring scraping on restricted surfaces |
| Full-page screenshot | Entire scrollable rendered page | Hidden code, machine-readable metadata, network context | Medium-high for layout context | Medium | Same rights issues as screenshots generally. citeturn35view0 | Lazy-loaded sections may still fail or differ | Product/listing pages where full visual record matters | Treating it as a source-code substitute |
| Viewport screenshot | Current screen region only | Most surrounding context | Low-medium | Low | Similar to manual screenshot | High omission risk | Fast proof of a specific placement | Any use needing full context |
| HTML save | Source HTML delivered or saved | Dynamic post-load state unless separately captured | Medium for text/markup | Low-medium | Often higher copyright/terms risk than screenshots; can be a fuller copy. citeturn36view3turn36view2turn13view0 | May not include runtime DOM | Structured text, source tags, reproducible parsing | Assuming it matches what users saw |
| Rendered DOM capture | Post-JS DOM state | Network headers, some hidden resources, visual CSS fidelity | Medium-high for rendered text state | Medium | Similar to HTML plus automation concerns | DOM after scripts can be timing-sensitive | JS-heavy pages where text changed after load | Using DOM as if it proves layout |
| Raw HTTP response capture | Status, headers, body bytes, redirects | Client-rendered post-load changes | High for protocol-level evidence | Medium | Potentially higher if it stores full body/headers with personal data | Redirect chains, session/state complexity | Status/headers verification, API/raw page response integrity | Claiming rendered page equivalence |
| Text extraction | Plain text content | Layout, styling, context, hidden text choices | Low-medium | Very low | Lower copyright risk if excerpted minimally; higher if fulltext retained extensively. citeturn36view2 | Parsing errors, lossy extraction | Searchable excerpts, comparisons | Visual-placement claims |
| Metadata extraction | Title, description, canonical, OG tags, etc. | Page body and visuals | Medium for citation metadata | Very low | Usually lower risk | Tags may be stale or inconsistent | Citation support, normalization | Substituting for actual page evidence |
| Structured data extraction | JSON-LD, microdata, RDFa | Visible text authenticity, full layout | Medium for machine-readable assertions | Very low | Usually lower risk than full copies | Markup can diverge from visible text | Merchant/listing evidence, rich-result context | Assuming structured data equals visible page |
| Headers/status capture | HTTP status, selected headers | Body/layout | Medium-high for transport facts | Very low | Generally lower if limited to metadata | Some browser APIs hide security/cookie headers. citeturn35view1 | Redirect/error proof | Content claims |
| Hash-only capture | Digest of a stored artifact | The artifact itself | Low by itself, high as integrity supplement | Very low | Low | Worthless without method + artifact reference | Integrity checking | Trying to prove content from hash alone |
| Wayback/third-party archive reference | External archived URL plus timestamp | Your own custody of underlying bytes unless separately stored | Medium for citation; varies by archive | Very low | Depends on archive’s terms and trustworthiness | External dependence, replay incompleteness | Reference-only backups, public citations | Sole evidence for disputed platform state |
| PDF print/save | Print-rendered page, often with headers/footers | Hidden code, some dynamic elements, full fidelity | Medium | Medium | Redistribution/copyright risk still applies | Print CSS can alter appearance | Human-readable report exhibits | Claiming exact browser fidelity |
| Video / screen recording | Temporal interaction and scrolling | Precise underlying markup/headers | Medium-high for flow and transient UI | High | Copyright/privacy can increase if more content is captured | Harder to index and compare | AI answers, interactions, ephemeral UI | Long-term routine archival of mundane pages |
| Provider API result snapshot | Licensed structured payload | Non-API-only visual state unless documented separately | High when API is official and rights-granted | Low-medium | Often preferred if terms authorize storage/use. citeturn28view0turn39search0turn39search2turn39search1 | API version drift | Metadata truth, repeatable monitoring | Visual-layout proof |
| SERP API raw payload | Licensed search-result payload, and sometimes HTML/screenshot | Native first-party page behavior outside payload | High for licensed monitoring | Low-medium | Better than unlicensed scraping, but still bounded by provider license. citeturn31view3turn31view1 | Search context emulation may differ from live user sessions | Search observation at scale | Treating payload as universal ground truth |

**Bottom line:** for Observatory evidence, the practical sweet spot is usually **full-page screenshot + limited normalized fields + hash + context metadata**, with **official API payloads** used where available and licensed. Full HTML/body retention should move into a separately governed exception class. citeturn35view0turn31view3turn19view0

### Evidence Quality and Fidelity

| Method | Visual Fidelity | Text Fidelity | Metadata Fidelity | Hashable? | Report-Friendly? | Caveat |
| --- | --- | --- | --- | ---: | ---: | --- |
| Viewport screenshot | High for visible region | Medium | Low | Yes | High | Great for “what was on screen,” terrible for “what the whole page contained.” citeturn35view0turn34view5 |
| Full-page screenshot | High | Medium | Low | Yes | High | Stronger visual context, but still no headers/code. citeturn35view0 |
| HTML source | Low | High for delivered source | Medium | Yes | Medium | May not reflect JS-rendered state. citeturn31view3turn34view7 |
| Rendered DOM | Medium | High for post-load text | Low-medium | Yes | Medium | Timing-sensitive and not necessarily stable across sessions. citeturn23view0turn35view2 |
| Raw HTTP response | Low | High for delivered bytes | High | Yes | Low-medium | Best for headers/status/hash integrity, not for human-facing reports. citeturn35view1turn35view2 |
| Text extraction | None | Medium-high | Low | Yes | High | Easy to quote and compare, easy to lose context. citeturn36view2 |
| Metadata extraction | None | Low | Medium-high | Yes | Medium | Good support evidence, not sufficient alone. citeturn21view2 |
| Structured data extraction | None | Medium for declared fields | Medium | Yes | Medium | Markup can diverge from visible text; Google says it should match visible text. citeturn35view3turn23view0 |
| PDF print/save | Medium | Medium-high | Low-medium | Yes | High | Print styles can materially change layout. citeturn30search16 |
| Third-party archive reference | Variable | Variable | Variable | Archive-specific | High | Reliability depends on the archive and replay quality. citeturn20view1turn19view0turn33search0 |
| Official API payload | Low visual | High for licensed fields | High | Yes | High | Best for normalized facts, not for visual SERP/page appearance. citeturn28view0turn39search3turn39search2turn39search7 |

The most **reproducible** methods are official API payloads, raw HTTP captures, and well-documented screenshot pipelines with fixed browser/device settings. The easiest methods to **tamper with** are screenshots and exported text when they are decoupled from provenance metadata and hashes. The best methods for **customer-facing citation** are screenshots, short excerpts, and stable third-party archive references—not raw protocol logs, unless the client enjoys reading headers for fun, which is a niche hobby at best. citeturn34view3turn34view5turn20view2turn19view0

### Legal / Terms / Copyright / Robots Considerations

**Required caveat:** publicly visible does not automatically mean unrestricted storage, redistribution, or automation rights. Robots.txt is a crawler-coordination standard, not an authorization system. Google says this directly, and RFC 9309 says the same in standards language: robots rules are requests to automated clients, not access authorization. citeturn21view0turn21view3

Public availability also does **not** erase copyright, privacy, contract, or platform terms. The U.S. Copyright Office explains that copyrighted works remain protected unless a permission, exception, or limitation applies, and that fair use is fact-specific. For personal data, the ICO guidance is a useful cautionary analogue: even when data is publicly available, data protection obligations do not vanish merely because it was public. citeturn36view3turn36view2turn34view0

Internal evidence storage is usually lower risk than customer-facing redistribution, but it is not zero risk. Internal copies still implicate reproduction/storage questions; external reports add display, distribution, and potential downstream republication risk. The bigger you copy and the more you share, the more trouble comes to dinner. citeturn36view2turn36view3

| Issue | Risk | Applies To | Mitigation | Needs Confirmation? |
| --- | --- | --- | --- | ---: |
| Assuming public means unrestricted | High | All page captures | Treat public display as visibility only; separately assess terms, copyright, privacy, and automation. citeturn36view3turn34view0 | No |
| Robots.txt treated as permission | High | Crawling/automation | Treat robots as crawl guidance, not legal authorization or privacy consent. citeturn21view3turn21view0 | No |
| Full-page copying of copyrighted content | High | HTML saves, PDFs, archive copies | Prefer screenshot, excerpt, metadata, or archive reference unless a stronger right exists. citeturn36view2turn36view3 | Sometimes |
| Redistribution of screenshots/page copies in client reports | Medium-high | Reports, exports, dashboards | Minimize displayed content; use excerpts or snapshots with source attribution and caveats. citeturn36view2 | Yes |
| UGC comments/reviews retained in bulk | High | Marketplace/social captures | Avoid bulk retention; prefer counts, excerpts, redaction, or reference-only. citeturn37view0turn34view0 | Yes |
| Public personal data captured because “it was there” | High | Screenshots, HTML, comments | Redact usernames, faces, contact info, minors, health/financial/legal signals where avoidable. citeturn34view0turn34view2turn37view0 | No |
| Automated capture on restricted platforms | High | Browser automation, scraping | Prefer official APIs; honor terms/rate limits/robots; define stop conditions. citeturn13view5turn13view0turn25search7turn12view7turn38view4 | No |
| Manual observation vs automation conflation | Medium-high | Compliance posture | Classify methods distinctly; manual allowance does not imply automation allowance. citeturn13view5turn13view0turn25search7 | No |
| Third-party archive reliance | Medium | Archive references | Use trusted archives; record archive timestamp; do not assume completeness. citeturn20view1turn20view2turn19view0 | No |
| Archive.today reliance | High | Reference-only workflows | Avoid as a preferred evidence archive; trust concerns are material. Third-party claim. citeturn33search0 | No |
| Storing Google Maps/Business Profile content outside allowed terms | High | Maps/local results/reviews | Use allowed APIs for owned profiles; avoid scraping/caching/resharing Maps content. citeturn12view7turn28view1 | No |
| Fair use assumed categorically | High | Reports and archival copies | Do not rely on blanket assumptions; case-specific review. citeturn36view1turn36view2 | Yes |

## Platform and Archive Boundaries

### Platform-Specific Capture Boundaries

| Surface | Manual Observation | Screenshot Risk | HTML Storage Risk | Automation Risk | Preferred Source |
| --- | --- | --- | --- | --- | --- |
| Google SERPs | Yes, pages are publicly viewable | Medium for internal evidence; higher if redistributed broadly | High; first-party search pages are especially terms-sensitive | High; Google actively detects automated queries, and official programmable options are not equivalent to unrestricted Search scraping. citeturn16search7turn16search10turn16search2 | Licensed SERP API payloads or manual screenshots. citeturn31view3turn31view1 |
| Bing SERPs | Yes | Medium | High | Medium-high; official old Bing Search APIs were retired in 2025. citeturn17search5 | Licensed SERP API payloads; manual screenshots where needed. citeturn31view6 |
| Etsy listings/search | Yes | Medium for internal evidence | High; Etsy terms expressly ban crawling, scraping, or spidering pages without permission. citeturn13view0 | High; Etsy API terms also prohibit automated scraping absent written authorization. citeturn12view6 | Etsy Open API where applicable; otherwise manual, minimal capture. citeturn39search2turn39search11 |
| Fiverr gigs/search | Yes | Medium | Medium-high | **Unclear — needs legal/terms confirmation** for specific capture/storage boundaries from current public terms text; official scraping prohibition was not cleanly surfaced in fetched terms. citeturn12view0 | Manual observation unless Fiverr provides a specific permitted interface |
| Shopify public storefronts | Yes | Medium | Medium; rights depend heavily on merchant site terms and robots in addition to Shopify ecosystem rules | Medium; public storefronts are merchant-owned surfaces, not a single universal capture license | Merchant page observation; Storefront API only where owner authorization exists. citeturn27search0turn27search3turn12view4 |
| Pinterest pins/boards/search | Yes | Medium | Medium-high | High; Pinterest terms/guidelines prohibit undocumented or unsupported scraping and automated extraction unless expressly permitted. citeturn25search3turn25search7 | Pinterest API for authorized content/account use. citeturn39search7turn39search1 |
| YouTube videos/channels/search | Yes | Medium | High | High; YouTube terms bar automated means except public search engines per robots.txt or written permission. They also restrict harvesting identifying information such as usernames or faces. citeturn13view5 | YouTube Data API for metadata; screenshots only when necessary. citeturn39search0turn39search3 |
| Reddit public posts/comments | Yes | Medium | Medium-high because UGC and usernames are sensitive even when public | Medium-high; Reddit’s public-content posture is “open, not unrestricted,” and API terms restrict commercial/API uses, AI training, and require deletion of stored content on termination. citeturn37view0turn38view4 | Official Reddit API or reference-only; avoid bulk comment capture |
| Google Business Profiles / local results | Manual viewing is possible in Search/Maps | Medium | High | High if derived from Maps content; Maps terms prohibit scraping, storage, and copying of many content classes outside allowed services. citeturn12view7 | Business Profile APIs for owned/managed listings; otherwise minimal manual evidence. citeturn28view0turn28view1 |
| AI answer surfaces | Usually yes | Medium and often the best option | Medium-high; HTML often unstable and rights unclear | High if using automation against consumer UI without permission | Manual screenshot or screen recording with strong context metadata. Google’s AI feature controls are still Search controls, not a blank check for copying. citeturn23view0 |

**Surface-specific takeaways:**

For **Google and Bing SERPs**, the clean path is licensed SERP data providers for repeatable monitoring, not DIY scraping. DataForSEO documents support for raw HTML, advanced parsed output, screenshots, device/location parameters, and short retention windows for screenshot URLs and standard HTML task results. That is not the same as Google or Microsoft blessing every downstream reuse, but it is materially safer than hammering first-party SERPs with unlicensed automation. citeturn31view1turn31view3turn31view6

For **marketplaces and social platforms**, screenshots for internal evidence are usually more defensible than bulk HTML retention, because they are narrower, more obviously contextual, and easier to redact. That said, once you capture reviews, usernames, profile photos, or faces, the privacy and UGC risk jumps. Pinterest, Etsy, and YouTube are all explicit that automation without permission is a bad idea. Reddit is “public,” but also tells you out loud that public does not mean unrestricted misuse. citeturn25search7turn12view6turn13view5turn37view0

### Third-Party Archive Options

| Archive Tool | Captures | API? | Strength | Risk | Observatory Use |
| --- | --- | ---: | --- | --- | --- |
| Internet Archive Wayback Machine | Archived replay of saved/crawled pages; URL-based historical references | Yes | Strong public citation utility; can support affidavits/certified records requests; Memento-compatible. citeturn20view1turn20view2 | Incomplete replay, robots/site-owner exclusions, JS gaps. citeturn20view2 | Good **reference-only** option; not a substitute for your own provenance |
| Save Page Now | One-time capture of a specific page | Via Wayback tooling/API ecosystem | Useful for point-in-time reference | Same replay/availability limits as Wayback | Good as supplementary external reference. citeturn20view1turn20view2 |
| Perma.cc | Creates archives with downloadable WARC/WACZ and screenshot captures; public/private archive controls | Yes | Very strong citation-oriented design, especially for legal/scholarly references. Public archive endpoint available; private storage possible. citeturn19view0 | Coverage and institutional orientation may make it less universal than Wayback | Strong candidate for **reference-only** or controlled external backup |
| Memento protocol | Time-based access framework across archives | Yes | Useful interoperability layer | Depends on participating archives | Good discovery/reference layer, not an archive by itself. citeturn20view1 |
| Archive-It / commercial archiving | Managed web archiving services | Yes/varies | Stronger organizational controls and custody | Cost, rights, scope, vendor dependence | Possible future enterprise option; evaluate contracts first. citeturn20view1 |
| Browser-local save tools | Local HTML/PDF/screenshot preservation | Usually no standardized archival API | Handy for manual capture | Weak provenance unless supplemented with hashes/metadata | Only for manual evidence workflows, not core archival truth |
| archive.today / archive.ph | On-demand public captures | Unclear / unofficially exposed in the wild | Historically convenient | Current trust and integrity concerns are material; third-party reporting tied to DDoS and archive tampering. citeturn33search0 | **Not preferred** |

Third-party archives are best used as **reference amplifiers**, not as your sole evidentiary spine. Wayback is useful because it is widely recognizable and supports stable archived URLs; Perma.cc is useful because it is built around citation durability and exposes downloadable archive artifacts including WARC/WACZ plus screenshot capture metadata. Archive.today is the opposite of what you want after a trust incident: fast once, expensive forever. citeturn20view1turn20view2turn19view0turn33search0

## Integrity, Privacy, and Storage Boundaries

### Hashing and Evidence Integrity

**Required principle:** a hash can prove that a stored artifact has not changed since hashing; it does not prove the artifact was lawfully captured or universally representative. NIST’s Secure Hash Standard supports the integrity claim, not the legal legitimacy claim. citeturn11search17turn11search10

Hashes are useful for screenshots, PDFs, HTML files, raw payloads, extracted text, and metadata bundles. They are most useful when paired with capture metadata and a clear statement of **what bytes were hashed**. They become much less useful when you hash unstable or non-canonical material from dynamic pages without documenting normalization. citeturn11search17turn34view3

Dynamic pages complicate hashing because visually identical pages can differ in embedded timestamps, nonce values, ad units, tracking parameters, and lazy-loaded resources. This is why canonicalization matters: hash the exact stored artifact, and if you also hash normalized text or metadata, record the normalization rules separately. Do not pretend that a normalized hash and a raw binary hash mean the same thing. citeturn10search7turn34view7

| Artifact | Hash Useful? | What It Proves | What It Does Not Prove | Caveat |
| --- | ---: | --- | --- | --- |
| Screenshot PNG/JPEG | Yes | Stored image bytes stayed unchanged since hashing | That the screenshot was authentic, complete, or lawfully captured | Strong only with provenance metadata. citeturn11search17turn34view3 |
| PDF | Yes | Stored PDF stayed unchanged | That PDF rendering matched browser exactly | Print CSS/layout drift is a real caveat. citeturn30search16turn11search17 |
| Raw HTML/body | Yes | Delivered body bytes stayed unchanged | That JS-rendered page matched the raw body | Distinguish raw response from rendered DOM. citeturn34view7turn35view2 |
| Raw HTTP response bundle | Yes | Status/headers/body bundle stayed unchanged | Lawfulness, authenticity, representative user experience | Very strong integrity evidence for protocol facts. citeturn35view1turn11search17 |
| Extracted text | Yes | That exact extracted text stayed unchanged | That extraction was complete or context-preserving | Record extraction method/version. |
| Structured data blob | Yes | Declared machine-readable fields stayed unchanged | That fields matched visible text or legal rights to reuse them | Google expects structured data to match visible content. citeturn35view3turn23view0 |
| Metadata bundle | Yes | Metadata record stayed unchanged | That metadata was correct when captured | Canonicalize field order/serialization before hashing |
| Hash-only reference | Limited | Integrity of a known artifact if artifact is elsewhere available | Content, provenance, rights, authenticity, completeness | Not enough as standalone evidence. citeturn11search17 |

### Privacy and Personal Data Risk

**Required boundary:** customer/private data and sensitive personal data should not be stored in Observatory merely because it appeared on a public page.

That boundary is stricter than “but it was public,” and it should be. Public availability does not erase privacy risk. The ICO guidance is explicit that public-source data still triggers obligations and that blanket collection of personal data from publicly available sources is likely unfair and contrary to data minimization principles. Reddit’s public content policy similarly says public content is visible, but not free for unrestricted misuse, especially for profiling, surveillance, or sensitive inferences. COPPA adds extra sensitivity where children under 13 are involved. citeturn34view0turn37view0turn34view2

For Observatory purposes, the riskiest “public but sensitive” categories are: usernames tied to controversial statements; profile photos and faces; review author identities; social comments; contact info; precise location information; minors in thumbnails or posts; health, legal, financial, political, sexual-orientation, and other sensitive inference categories; and any customer or order data accidentally exposed on public pages. YouTube’s general terms specifically call out harvesting information that could identify a person, including usernames or faces, as a restriction absent permission or a specific exception. citeturn13view5turn37view0turn34view0

**Practical privacy line:** if a capture is useful without the personal data, remove or do not store the personal data. If a claim can be supported by counted or normalized evidence rather than raw user comments, keep the count, not the comments. If a screenshot must be retained, consider redacted derivatives for routine use and restrict the unredacted original to exception handling, if retained at all. citeturn34view0turn37view0

### Raw vs Normalized vs Reference-Only Capture

| Target | Raw Store? | Normalized? | Screenshot? | Hash? | Reference Only? | Notes |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Public product/listing page | Conditional | Yes | Yes | Yes | Sometimes | Usually screen + normalized fields beats full HTML copy. Copyright/merchant terms still matter. citeturn36view2turn27search0 |
| SERP result | Prefer licensed payload only | Yes | Yes | Yes | Yes | Prefer SERP API payloads/screens over first-party HTML copying. citeturn31view3turn31view1 |
| AI answer page/screenshot | No by default for raw page copy | Yes, narrow excerpt only | Yes | Yes | Sometimes | Manual screenshot often the cleanest evidence of ephemeral UI. citeturn23view0 |
| YouTube video metadata | Prefer API payload | Yes | Sometimes | Yes | Yes | Use official API for metadata; avoid storing comments unless truly necessary. citeturn39search3turn13view5 |
| Marketplace review/comment | Generally no | Maybe summary/count only | Redacted only if needed | Yes | Preferred | High privacy/UGC risk. citeturn37view0turn34view0 |
| Public Shopify product page | Conditional | Yes | Yes | Yes | Sometimes | Merchant-owned content; owner/site terms and robots matter. citeturn27search0turn12view4 |
| Competitor article/blog page | Generally no full raw copy | Yes, limited excerpt | Yes | Yes | Preferred | High copyright risk for full-text/full-HTML retention. citeturn36view2turn36view3 |
| Provider API response | Yes, if license allows | Yes | Optional | Yes | Sometimes | Best evidence class for repeatable machine-readable observation. citeturn28view0turn39search3turn39search2 |
| Terms/pricing documentation page | Conditional | Yes | Yes | Yes | Yes | Often worth preserving because it supports rights and vendor-change evidence, but still not “copy everything by default.” |
| Google Business Profile content | Only for owned/API-authorized data | Yes | Sometimes | Yes | Often | Maps content has hard restrictions on scraping, caching, and reuse. citeturn12view7turn28view1 |

The clean pattern is: **raw only when rights and purpose are clear; normalized whenever the fact can be abstracted safely; screenshot when visual state matters; hash for every retained artifact; reference-only when the copy would be riskier than the citation.** citeturn20view1turn19view0turn36view2

### Chain of Custody / Provenance Needs

NIJ’s chain-of-custody guidance maps almost perfectly onto Observatory evidence needs: record what the evidence is, where it came from, who touched it, and how tampering is prevented or detected. For digital page evidence, that means provenance metadata is not “nice to have.” It is the difference between a useful record and a screenshot that wandered in off the street claiming to be important. citeturn34view3

| Metadata Field | Purpose | Required? | Caveat |
| --- | --- | ---: | --- |
| Capture timestamp with timezone | Anchors time-bound claim | Yes | UTC plus local timezone is best |
| Capture operator / tool | Distinguishes manual, automated, API, archive reference | Yes | Tool version matters if reproducibility matters |
| URL | Identifies observed page | Yes | Record actual requested URL |
| Canonical URL | Distinguishes alternate/tracking URLs | Recommended | Not always available or reliable |
| HTTP status | Shows whether page loaded, redirected, errored | Recommended | Essential for raw/API captures. citeturn35view1 |
| Selected headers | Supports protocol context | Recommended | Avoid needlessly storing sensitive headers/cookies |
| Browser / device / viewport | Explains rendering context | Yes for screen captures | Especially important for SERP/mobile differences. citeturn35view0turn31view3 |
| Location / language | Explains result variation | Recommended | Essential for SERP and marketplace localization. citeturn31view3turn39search9 |
| Account / login state | Explains personalization/private leakage risk | Yes when applicable | Never capture private/customer pages in routine workflows |
| Robots / terms status check | Shows whether rights review occurred | Recommended | Not proof of permission; just review trace |
| Capture method | Defines what the artifact can actually prove | Yes | Core evidentiary field |
| Artifact hash | Integrity of stored file | Yes if artifact stored | State algorithm used. citeturn11search17 |
| Screenshot hash | Integrity of screenshot | Yes if screenshot stored | Useful for downstream report verification |
| HTML/body hash | Integrity of source artifact | Conditional | Only where body retained |
| External archive URL | Preserves public citation path | Conditional | External services can change or disappear |
| Rights / retention class | Governs storage/display/expiry | Yes | Critical policy hook |
| Redaction status | Shows whether personal data was removed | Yes when relevant | Keep original-and-redacted distinction clear |
| Notes / caveats | Records anomalies, consent issues, timing problems | Recommended | This is where the honest caveats live |

## Claim Language, Manual Rules, Automation, and Recommendations

### Safe and Unsafe Claim Language

| Evidence | Safe Wording | Unsafe Wording | Required Caveat |
| --- | --- | --- | --- |
| Screenshot | “A screenshot captured on [date/time] shows URL U displaying X in viewport/context C.” | “The page always displayed X.” | Snapshot is time- and context-bound. citeturn34view5turn34view3 |
| Full-page screenshot | “A full-page screenshot captured at T shows the rendered page as observed by tool/browser B under settings C.” | “This is the complete truth of the page for all users.” | Full-page still depends on rendering context and may omit failed/lazy resources. citeturn35view0turn20view2 |
| HTML/body artifact | “The stored HTML/body artifact captured at T contained phrase X.” | “The site currently says X.” | Raw body may differ from rendered DOM. citeturn31view3turn35view2 |
| Text extraction | “Extracted text from the stored artifact included X at capture time T.” | “The visible page definitely said X exactly this way.” | Extraction is lossy and context-sensitive |
| API payload | “The official API response returned field Y=Z at time T.” | “The public UI necessarily displayed Z.” | API facts and UI facts are related, not identical. citeturn28view0turn39search3 |
| Hash | “The artifact hash matches the archived copy stored by Observatory.” | “The hash proves the page was authentic.” | Hash proves integrity of the stored artifact, not authenticity or lawfulness. citeturn11search17 |
| Archive reference | “A Wayback/Perma reference exists for URL U at archived time T.” | “The archive is a perfect copy of the live page.” | Archived replay may be incomplete. citeturn20view2turn19view0 |

### Manual Capture Rules

These are **candidate contract inputs**, not doctrine.

Record the URL, timestamp, timezone, browser/device/viewport, language/location, and whether the page was logged in or personalized. Capture enough surrounding context that a later reviewer can tell what the screenshot actually shows. Hash the artifact after capture. Keep manual evidence labeled as manual evidence, distinct from provider/API evidence. Do not use manual capture to launder recurring scraping into “it was just a lot of clicking.” citeturn34view3turn35view0

Avoid logged-in, private, customer, checkout, inbox, or account-management pages. Avoid capturing sensitive personal data unless there is a specifically approved reason and a redaction plan. Avoid bulk comment/review harvesting. If the evidence target is a restricted platform, prefer an official API or do not capture beyond minimal manual observation. citeturn34view0turn13view5turn13view0turn25search7turn12view7

For manual captures of volatile surfaces such as AI answers, SERPs, or interactive marketplace widgets, consider capturing both a screenshot and a short operator note describing the action sequence needed to reach the displayed state. That is cheap provenance insurance. citeturn23view0turn34view3

### Automation and Anti-Scraping Risk

**Required rule:** automation must not be assumed safe merely because manual observation is possible.

That distinction is explicit in platform terms. YouTube bars automated access except limited permitted cases; Etsy bans crawling/scraping/spidering absent permission and separately bars automated scraping in API terms; Pinterest bans automated scraping/data extraction absent express permission; Maps terms prohibit scraping and many forms of caching/storage; Reddit’s API terms require explicit compliance, set limits, and restrict uses such as AI training without rightsholder permission. citeturn13view5turn13view0turn12view6turn25search7turn12view7turn38view4

| Method | Risk Level | When Acceptable | When Not Acceptable | Notes |
| --- | --- | --- | --- | --- |
| Manual observation | Low-medium | Ad hoc review of public pages with policy-compliant handling | Logged-in/private/customer pages; sensitive data capture | Still not blanket reuse permission |
| Official API access | Low-medium | When terms authorize the data and proposed storage/use | When proposed retention/display exceeds license | Preferred path for repeatable monitoring. citeturn28view0turn39search3turn39search2turn39search7 |
| Browser automation on unrestricted pages | Medium | When terms permit it or source owner authorizes it | When platform terms prohibit automation or rate/use is abusive | Rate limits and stop conditions still needed |
| Direct scraping / crawling of platform pages | High | Only where clearly allowed by terms and robots, with low-risk scope | Most major platform surfaces in this report | Default should be “no” unless clearly allowed |
| Continuous monitoring of SERPs via provider API | Medium | Licensed third-party provider with documented outputs/limits | If provider terms or downstream use rights are exceeded | Better than first-party scraping. citeturn31view3turn31view1 |
| Capture of UGC at scale | High | Rare exception with explicit legal/policy review | Default case | Privacy + copyright + platform risk compound quickly |
| Capture of Maps/Business review content | High | Owned-profile API workflows | General scraping/storage/caching | Maps terms are unusually restrictive. citeturn12view7 |

**Stop conditions** should include: robots or terms review fails; login/customer/private data appears; rate limiting or anti-bot signal appears; the surface is a platform page with express anti-automation language; required provenance fields cannot be supplied; or the method would capture material beyond the approved evidence scope. citeturn21view0turn13view5turn13view0turn25search7

### Recommended Observatory Handling

This research supports a fairly crisp boundary set.

**What belongs in the Capture Package Contract:** capture method classification; timestamp/timezone; URL/canonical; browser/device/viewport; location/language/login context; operator/tool; artifact list; hashes; redaction status; caveat statement; rights/review flag; and confidence label about what the method can prove. citeturn34view3turn35view0turn11search17

**What belongs in the Raw Archive / Payload Retention Contract:** decision classes for screenshot, API payload, raw HTML/body, PDF, extracted text, metadata bundle, and external archive reference; explicit distinction between default retention and exception retention; and a rule that full-copy retention needs a stronger rights basis than screen-level evidence. citeturn36view2turn19view0turn20view1

**What belongs in the Rights / Retention Contract:** source class; platform/API terms basis; redistribution class; storage class; retention horizon; whether UGC/personal data is present; whether archive-reference-only is required; and whether later display must use redacted derivatives. citeturn34view0turn37view0turn12view7turn24view0

**What belongs in the Evidence ID / Citation Contract:** stable evidence ID; artifact hash; capture timestamp; method label; source URL; archive link if any; and approved safe wording for downstream reporting. The key is that the citation should point to a stored observation object, not to an overconfident conclusion. citeturn34view3turn11search17

**What belongs in the Manual Evidence Capture Rules:** do/don’t rules for public-only surfaces; provenance minimums; redaction; no private/customer pages; no use of manual capture as a recurring scraping substitute; and a requirement to separate manual evidence from provider/API evidence. citeturn34view3turn34view0

**What belongs in Hammer Tests:** method mismatch tests, rights mismatch tests, privacy leak tests, stale reference tests, missing-metadata tests, dynamic-page hash drift tests, archive-replay incompleteness tests, and overclaim-language tests. citeturn20view2turn34view5turn11search17

**What should be reference-only:** third-party public pages where full copies add more legal risk than value; competitor articles/blog pages; pages already stably archived in Wayback/Perma where an external reference plus screenshot is enough; and certain platform-managed public pages where official APIs or archive references suffice. citeturn20view1turn19view0turn36view2

**What should be avoided:** bulk HTML copies of marketplace/social/search pages by default; bulk review/comment retention; storage of public personal data just because it was visible; reliance on archive.today as a preferred evidentiary archive; and any recurring automation on platforms with express anti-scraping language unless and until counsel says otherwise. citeturn13view0turn13view5turn25search7turn33search0

## Questions and Roadmap Inputs

### Questions / Unknowns To Confirm

**Unclear — needs legal/terms confirmation** for the following items:

Whether internal retention of full HTML copies of third-party public pages is acceptable across your target jurisdictions and customer/reporting model, especially where the source page is copyrighted editorial or UGC-heavy. The sources support caution, not a blanket yes/no. citeturn36view1turn36view2

Whether your intended use of screenshots in customer-facing reports is narrow factual quotation/commentary or broader republication, because the fair-use analysis changes with scope, commerciality, and amount used. citeturn36view1turn36view2

Whether manual screenshots of certain platform pages are acceptable for repeat operational monitoring at scale even when automation is restricted. Terms often speak clearly about automation and less clearly about repeated manual commercial capture/storage. Fiverr is especially one to confirm from current terms with counsel because the fetched terms text did not surface a crisp scraping clause the way Etsy, Pinterest, and YouTube did. citeturn12view0turn13view0turn13view5turn25search7

Whether any customer-specific workflow would ever justify retaining public-but-sensitive UGC artifacts unredacted. The research answer is “usually no,” but if there is a carve-out, it needs policy and legal review up front. citeturn34view0turn37view0

### Decision Inputs For M1 / M7 / M8 / M13 Roadmap

This research is **suitable as input** for: source admission criteria, evidence method ranking, rights classification, retention classes, redaction classes, report-safe language, manual-capture workflow design, and hammer-test design for claim overreach, privacy leakage, or rights mismatch. citeturn34view3turn36view2turn21view0

For a roadmap framing:

- **M1-type decisions** should settle the baseline observation doctrine: screenshot-plus-provenance as default, API payload where licensed, full-copy retention by exception only. citeturn31view3turn19view0
- **M7-type contract decisions** should settle rights/retention classes and evidence-safe claim language. citeturn36view2turn34view5
- **M8-type hammer decisions** should target dynamic pages, missing context, privacy leakage, and overconfident wording. citeturn20view2turn34view5
- **M13-type provider admission decisions** should require official API preference, platform-terms review, and explicit rejection of “manual is possible, therefore automation is fine.” citeturn24view0turn12view6turn25search7turn13view5

## Appendices

### Appendix Capture Method Comparison Table

This appendix consolidates the capture-method recommendation logic into a blunt ranking.

| Method | Observatory Default? | Keep Directly? | Hash? | Show in Reports? | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| Full-page screenshot | Yes | Yes | Yes | Yes | Best default general-purpose evidence artifact. citeturn35view0 |
| Viewport screenshot | Limited | Yes | Yes | Yes | Only when the claim is explicitly viewport-bound |
| Normalized metadata bundle | Yes | Yes | Yes | Yes | Lightweight and useful for citations |
| Official API payload | Yes when available | Yes | Yes | Sometimes | Best for repeatable facts, weaker for visuals. citeturn28view0turn39search3 |
| SERP API payload | Yes for SERP monitoring | Yes | Yes | Sometimes | Preferred to direct SERP scraping. citeturn31view3 |
| Raw HTTP response | Exception | Conditional | Yes | Rarely | Strong protocol evidence, higher burden |
| HTML/body copy | Exception | Conditional | Yes | Rarely | Higher rights burden than most teams admit |
| PDF print/save | Limited | Conditional | Yes | Yes | Good exhibit, not necessarily faithful browser replay. citeturn30search16 |
| Text extract | Yes, narrow | Yes | Yes | Yes | Use excerpt-first, not full-text-by-default |
| Third-party archive reference | Yes | No or minimal | Hash local citation record | Yes | Great supplement, not sole custody. citeturn20view1turn19view0 |
| Video/screen recording | Exception | Conditional | Yes | Rarely | Use for interactive/ephemeral states |

### Appendix Platform-Specific Boundary Table

| Surface | Preferred Evidence Pattern | Avoid |
| --- | --- | --- |
| Google SERP | SERP API payload + screenshot + context metadata | First-party scraping/copying of raw search pages |
| Bing SERP | SERP API payload + screenshot | Legacy assumptions about old Bing Search APIs |
| Etsy | Manual screenshot + normalized fields + API where allowed | Crawling/scraping/spidering pages or automated extraction without permission. citeturn13view0turn12view6 |
| Fiverr | Manual screenshot only, pending terms review | Any automation until terms position is confirmed |
| Shopify storefront | Screenshot + normalized product facts; owner-authorized API if available | Assuming Shopify-wide permission from public visibility |
| Pinterest | Manual screenshot or authorized API data | Unsupported scraping/data extraction. citeturn25search3turn25search7 |
| YouTube | API metadata + screenshot when visual context matters | Automated page capture outside permitted means; identity harvesting. citeturn13view5turn39search3 |
| Reddit | API/reference-only + minimal screenshot when necessary | Bulk comment retention or AI-training-style corpus capture. citeturn37view0turn38view4 |
| Google Business Profile / Maps | Owned-profile API data or minimal manual screenshot | Scraping/caching/store-and-reshare of Maps content. citeturn12view7turn28view1 |
| AI answer surfaces | Manual screenshot or screen recording + context note | Treating stored HTML as stable or complete |

### Appendix Hashing / Evidence Integrity Table

| Situation | Recommended Integrity Step | Why |
| --- | --- | --- |
| Stored screenshot | Hash exact binary; store algorithm and timestamp | Simple integrity proof. citeturn11search17 |
| Stored API JSON | Canonical JSON serialization + hash | Avoid meaningless differences from key order/formatting |
| Stored HTML/raw body | Hash exact bytes as received; if also normalized, hash normalized derivative separately | Separates raw integrity from normalized comparability |
| Stored text excerpt | Hash excerpt plus metadata bundle | Prevents quote drift |
| External archive reference | Hash your local citation record, not the third-party archive itself unless mirrored | You control the record you stored |
| Dynamic pages | Record capture context and artifact hash together | Hash without context is half a receipt |

### Appendix Safe vs Unsafe Claim Matrix

| Evidence | Safe Wording | Unsafe Wording | Required Caveat |
| --- | --- | --- | --- |
| Screenshot | “The capture shows…” | “The page was…” | Observed under specific context only |
| HTML artifact | “The stored HTML contained…” | “The site says…” | Raw source may differ from rendered state |
| API payload | “The API returned…” | “Users saw…” | API output is not always UI output |
| Hash | “The artifact has not changed since hashing…” | “The artifact was genuine…” | Integrity is not authenticity |
| Archive reference | “An archive reference exists…” | “The archive proves exactly what the live page was…” | Replay can be incomplete |

## Decision-Ready Summary

Recommended status:

- **suitable as Capture Package Contract input** — **Yes**. The research is strong enough to define capture classes, provenance minimums, and evidence-safe claim boundaries. citeturn34view3turn35view0
- **suitable as Raw Archive / Retention Contract input** — **Yes**. Especially for direct-store vs hash-only vs reference-only vs avoid decisions. citeturn36view2turn19view0
- **suitable as Rights / Retention Contract input** — **Yes, with legal review gates**. Terms and copyright issues are real and source-specific. citeturn13view0turn13view5turn25search7turn36view2
- **suitable as Hammer Matrix input** — **Yes**. The failure modes are clear: overclaiming, privacy leakage, missing provenance, method mismatch, and automation creep. citeturn34view5turn34view0turn11search17
- **needs legal/terms confirmation** — **Yes** for full-copy retention, customer-facing screenshot redistribution, ambiguous marketplace/platform edges, and jurisdiction-specific privacy treatment. citeturn36view1turn36view2turn34view0
- **needs owner ruling** — **Yes** on whether Observatory’s default should ever permit raw HTML retention for third-party pages, and on whether UGC should be reference-only by default.  
- **not recommended / avoid** — bulk platform-page copying by default, recurring automation on restricted surfaces, archive.today as a preferred archive reference, and storing sensitive public personal data merely because it appeared on screen. citeturn33search0turn13view5turn13view0turn25search7turn34view0

**Must know before M7 contracts**

You need an owner decision on default allowed artifact classes; a legal answer on full-page HTML/body retention; a rights taxonomy separating internal evidence from report redistribution; and a rule for UGC/comments/reviews. citeturn36view2turn37view0

**Must know before M8 hammers**

You need explicit failure tests for missing timestamp/context, dynamic rendering drift, screenshot cropping, hash-without-artifact nonsense, personal-data leakage, and claims that overstate what an artifact proves. citeturn20view2turn34view5turn11search17

**Must know before provider/source admission**

You need official-API preference rules, current terms review, robots posture review, and a hard rejection path for surfaces with express anti-automation language unless there is written permission or clear alternative rights. citeturn13view5turn12view6turn25search7turn12view7

**Must know before manual evidence capture workflow**

You need minimum provenance fields, redaction standards, no-private-page rules, and operator wording standards for what the evidence can and cannot claim. citeturn34view3turn34view0

**Must know before customer-facing reports**

You need a redistribution standard for screenshots/excerpts, archive-reference citation rules, and approved safe wording that avoids “always/currently/authentic/universal” overclaims. citeturn36view2turn34view5

**Must know before any automation**

You need a surface-by-surface acceptability matrix, rate/stop conditions, API-first alternatives, and a policy that manual observation does not imply automation permission. citeturn13view5turn13view0turn25search7