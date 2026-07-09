# GEO / AI Citation Surface Research Report for The Observatory

## Executive Summary

The short version: AI citation visibility is measurable, but only as **prompt/context/time-bound observation**. It is not a stable ranking signal, not proof of authority, not proof of endorsement, and definitely not a reason to turn The Observatory into a shrine to third-party scores. A citation is a footprint, not a halo. Official product docs across Google, OpenAI, Microsoft, Perplexity, Google Gemini, Anthropic, and DataForSEO all support the same operational truth in different words: these systems are probabilistic, can make mistakes, can vary by query and context, and often expose citations or links only inside product-specific experiences or APIs. citeturn27view0turn28view0turn10view0turn24search8turn17search12turn26search8turn30search1

For The Observatory, the safest early evidence class is **public, externally observable AI/search output captured with provenance**: surface name, query/prompt, timestamp, country/language/device if known, login state if known, answer presence/absence, and the exact cited URLs/domains shown at capture time. Google AI Overviews/AI Mode, Bing/Copilot AI answers, ChatGPT search-connected answers, Perplexity answers, Gemini answers grounded to Google Search, and official provider APIs that return citation metadata all fit this model in different degrees. citeturn27view0turn27view1turn27view2turn15view0turn15view1turn17search12turn26search8turn30search0

The big boundary is this: **store observations, not conclusions**. Safe storage candidates include observed answer presence, observed cited/source-linked URLs and domains, provider name, model/product/version when exposed, prompt wording, location parameters when set, and provider-returned metadata. Unsafe or out-of-scope defaults include customer prompt logs, customer analytics, account-personalized histories, proprietary tool “visibility scores” treated as facts, and any automation path that depends on scraping consumer UIs against terms. OpenAI’s consumer Terms of Use expressly prohibit automatically or programmatically extracting data or output from the Services, and DataForSEO itself labels part of its AI Optimization offering as a “scraper” for ChatGPT search. That is a bright yellow flag, not a green light. citeturn10view0turn7view1turn4view4turn5view0

The newest hard fact that materially changes the Google boundary: Google Search Console now has a **Generative AI performance report for Search** rolling out to a subset of verified site owners, covering impressions in **AI Overviews and AI Mode**, while Search Labs experiments remain excluded. That means Google now offers owner-facing reporting for gen-AI Search visibility, but it is still **impression reporting**, not a public live-capture API for AI Overview or AI Mode answers. citeturn27view2turn27view3turn29search3

The newest hard fact that materially changes the Microsoft boundary: Bing Webmaster Tools now has an **AI Performance** report in public preview showing when a site is cited in AI-generated answers across Microsoft Copilot, AI-generated summaries in Bing, and select partner integrations. Microsoft describes these as citation-oriented visibility metrics, explicitly not traditional ranking metrics. That makes Bing unusually advanced on owner-facing AI citation telemetry, but the official Bing Webmaster API documentation reviewed here does not document a matching AI-performance export endpoint. citeturn25search1turn25search2turn21search6

The main research conclusion is therefore strict and boring in the best possible way: **The Observatory should admit only evidence that can be traced back to a surface, a provider, a timestamp, and a reproducible capture context. Everything else is interpretation, estimate, or testimony.** citeturn38view1turn38view0turn38view2turn38view3

## Confidence and Source Quality

This report is built primarily on **official product documentation, official help centers, official developer docs, official pricing/help pages, and official webmaster/platform announcements** from Google, Microsoft, OpenAI, Perplexity, Anthropic, Brave, DataForSEO, Semrush, Ahrefs, and the vendors discussed in the third-party tooling section. All cited web sources were accessed on **July 8, 2026** unless the source itself states another publication date. citeturn27view0turn27view1turn27view2turn10view0turn13view0turn17search12turn26search8turn30search0turn31search0turn4view0

Confidence is highest where an official source directly states product behavior, API support, or terms constraint. Confidence is medium where a provider’s official materials describe a capability but do not fully specify downstream storage/redistribution rights. Confidence is lower where the market relies on vendor marketing pages instead of formal docs, or where an official terms/help page exists but was not fully retrievable in this environment. Those cases are marked as **Unclear — needs confirmation.** citeturn17search0turn18search0turn35search3turn36search1

Third-party research on volatility and citation reliability materially reinforces the doctrine. A 2026 statistical framework paper argues that identical queries on generative search platforms can produce different cited sources and that single-run visibility metrics are misleadingly precise; a 2025 *Nature Communications* study found that between 50% and 90% of evaluated LLM responses were not fully supported by the sources they cited in a medical setting; and a 2026 audit found evidence of AI-generated sources appearing among citations across ChatGPT, Copilot, Gemini, and Perplexity. These are not edge-case warnings; they are the whole game. citeturn38view1turn38view0turn38view3

## Source List

Key official Google sources reviewed included Google Search Central’s guidance on AI features and websites, Google Search Help pages for AI Overviews and AI Mode, Google Search’s product pages for AI Overviews and AI Mode, and Search Console’s documentation for the Generative AI performance report and impression/click rules. citeturn27view0turn27view1turn27view2turn27view3turn28view0turn32view0turn33search0turn33search1

Key official OpenAI sources reviewed included ChatGPT Search Help, OpenAI’s consumer Terms of Use, the OpenAI API web search guide, and OpenAI developer documentation on crawler behavior. citeturn9search1turn10view0turn13view0turn15view0turn15view1turn9search19

Key official Microsoft sources reviewed included the Copilot transparency note, Microsoft 365 Copilot web-search behavior/help pages, Bing Search API retirement documentation, Grounding with Bing Search docs, Bing Webmaster API docs, Bing Webmaster Tools AI Performance help/blog pages, and Bing Webmaster Guidelines. citeturn24search0turn24search3turn21search2turn23search0turn23search2turn21search6turn25search1turn25search2turn25search14

Key official Perplexity sources reviewed included the Search API docs, Sonar/API docs, Agent API web search docs, streaming citation-parsing docs, privacy/security docs, and help-center materials describing citations in product answers. citeturn16search1turn16search13turn16search5turn16search4turn17search0turn17search12

Key official Gemini/Google AI sources reviewed included Gemini API grounding-with-Google-Search docs, Gemini app help on related sources, Gemini API billing and rate-limit/terms documentation. citeturn26search0turn26search8turn26search2turn26search3turn26search7turn26search19

Key official Anthropic sources reviewed included Claude’s web-search tool docs, citations/search-results docs, help pages on web search, and Anthropic’s crawler/search bot documentation. citeturn30search0turn30search2turn30search1turn30search20

Key official DataForSEO sources reviewed included SERP API docs, Google AI Mode SERP docs and pricing, AI Optimization overview, LLM Responses/LLM Mentions/ChatGPT LLM Scraper docs, result-storage rules, and terms of service. citeturn4view2turn4view1turn4view0turn7view0turn7view1turn7view2turn4view3turn4view4turn5view0

Key official third-party tool sources reviewed included product and pricing pages for Profound, Peec AI, Otterly, AthenaHQ, Semrush, Ahrefs, Rankscale, Scrunch, ZipTie, Nozzle, Goodie, Brave Search API, and related official help pages where available. citeturn34search20turn34search5turn34search2turn34search6turn34search3turn35search4turn35search0turn35search1turn35search5turn36search0turn36search4turn35search3turn35search7turn36search6turn35search2turn36search1turn31search0

## Surface Research

### AI / GEO Surface Overview

The major surfaces break into four evidence classes. First, **public answer surfaces with visible citations/links**: Google AI Overviews, Google AI Mode, Bing/Copilot search mode, ChatGPT search-connected answers, Perplexity answers, Gemini answers with web grounding, and Claude web-search responses. Second, **official APIs that can return grounded/citation-bearing output**: OpenAI web search API, Perplexity Search/Sonar/Agent APIs, Gemini API grounding with Google Search, Anthropic web search tool, Azure Grounding with Bing Search, Brave Search API, and several DataForSEO APIs. Third, **owner-facing telemetry surfaces**: Google Search Console’s generative AI performance report and Bing Webmaster Tools AI Performance. Fourth, **third-party observation layers**: DataForSEO and the AI visibility tools market. citeturn27view0turn27view1turn27view2turn9search1turn13view0turn17search12turn16search1turn26search8turn30search0turn23search0turn31search0turn25search1

The main evidence risks are remarkably consistent across providers: product variability, query fan-out/retrieval variability, region/language/account variation, model-version drift, undisclosed ranking/retrieval changes, and the difference between “was cited for this answer” and “is generally authoritative.” Google says AI Mode and AI Overviews may use different models and techniques and show different responses and links; OpenAI says output may not always be accurate and should not be relied on as a sole source of truth; Microsoft says Copilot can make mistakes and citations should be checked; Perplexity and Anthropic both position citations as verification aids, not guarantees. citeturn27view0turn27view1turn10view0turn24search8turn17search12turn30search1

| Surface | Citations or Links | Official API | Public or Private | Automation Risk | Evidence Risk |
| --- | --- | --- | --- | --- | --- |
| Google AI Overviews | Yes, supporting links/web links shown in product UI citeturn28view0turn27view0 | No documented public live-capture API found in reviewed Google Search docs; owner telemetry exists in Search Console citeturn27view2turn27view0 | Public surface; answer varies by context citeturn28view0turn27view0 | High if scraped; safer via manual capture or approved providers | Very high volatility; citation ≠ authority |
| Google AI Mode | Yes, helpful web links in answer flow citeturn27view1turn32view0 | No documented public live-capture API found in reviewed Google Search docs; owner telemetry exists in Search Console citeturn27view2turn27view1 | Public surface, but availability/context varies citeturn27view1turn32view0 | High if scraped; safer via manual capture or provider | Very high; multi-search fan-out and follow-up context matter |
| Bing Copilot / Bing AI answers | Yes, hyperlinked citations/sources in grounded responses citeturn24search0turn24search3 | No direct “Bing Copilot answer API” found; Bing Search APIs retired; Azure Grounding with Bing exists for developers citeturn21search2turn23search0 | Mixed: public Copilot UI plus private/admin surfaces | High for UI automation; lower via Azure tooling | High; citation data and answer text can drift |
| ChatGPT search | Yes, inline citations or Sources panel citeturn9search1turn9search4 | Yes, OpenAI web search tool / `gpt-5-search-api` citeturn13view0turn15view0 | Mixed: consumer product plus official API | Consumer UI automation is contract-risky; API safer | High; output probabilistic and search context configurable |
| Perplexity | Yes, citations/links are core product behavior citeturn17search12turn16search4 | Yes, Search API, Sonar API, Agent API citeturn16search1turn16search13turn16search5 | Mixed: public product plus API | Low via API; higher via UI automation | High; answer/citation set can vary |
| Gemini | Yes when grounded/when sources are shown citeturn26search8turn26search2 | Yes, Gemini API grounding with Google Search citeturn26search8turn26search0 | Mixed: consumer app plus API | Low via API; consumer UI capture should stay manual unless clearly allowed | High; source display is conditional and context-bound |
| Claude web search | Yes, every web-search response includes citations per docs/help citeturn30search0turn30search1 | Yes, Anthropic web search tool citeturn30search0 | Mixed: consumer product plus API | Low via API; UI automation risk depends on terms not fully reviewed here | High; search access and citations are context-bound |
| DataForSEO | Returns structured capture/provider metrics depending endpoint citeturn4view0turn7view1turn7view2 | Yes, official API suite citeturn4view0turn4view2 | Provider dataset/API | Low contract risk with DataForSEO itself, but upstream provider/engine constraints still matter citeturn5view0 | Mixed: direct capture, indirect capture, and proprietary estimates are all present |

### Google AI Overviews / AI Mode Evidence Ceiling

Google describes AI Overviews as AI-generated snapshots in Search with links to dig deeper, available in many countries and languages, and shown when Google’s systems determine generative AI would be especially helpful. Google describes AI Mode as its more powerful AI search experience, using query fan-out and follow-up conversation with helpful links to the web; the AI Mode product page says it uses Gemini 3 intelligence, while Search Central says AI Mode and AI Overviews may use different models and techniques and therefore show different responses and links. citeturn28view0turn27view1turn32view0turn27view0

From a site-owner perspective, Google’s official line is simple and actually useful: there are **no extra technical requirements** to appear as a supporting link in AI Overviews or AI Mode beyond normal Search eligibility with a snippet, and “the best practices for SEO remain relevant.” That means Observatory should not store any provider-interpretation that says “Google rewards X specially for AI Mode” unless Google itself documents it. In the reviewed docs, it does not. citeturn27view0

Google now provides two reporting layers relevant to evidence boundaries. First, Search Central says sites appearing in AI features are included in Search Console traffic and are reported within the Performance report’s **Web** search type. Second, Google added a dedicated **Generative AI performance report** for Search that is rolling out to a subset of site owners and includes impressions from **AI Overviews** and **AI Mode**; it excludes Search Labs experiments. Google’s impression rules further specify that links in AI Overviews count under standard visibility rules, and follow-up questions in AI Mode are treated as **new queries**. citeturn27view0turn27view2turn27view3

What Google does **not** document in the reviewed sources is a public Google Search API that returns live AI Overview or AI Mode answers/citation sets for arbitrary queries. That absence should be treated carefully: the safest phrasing is not “Google has no API, case closed,” but rather **“No public live-capture API for AI Overviews/AI Mode was found in the reviewed official Google Search docs.”** That is an inference from the reviewed documentation, not a universal negative claim. citeturn27view0turn27view2

Safe claim ceiling for Observatory: **For query X, in observed context C, Google displayed an AI Overview or AI Mode response at time T and surfaced source URL/domain Z among the displayed links.** Unsafe claim: **Google considers Z authoritative** or **Z ranks first in Google’s AI system.** Google itself says responses and links can vary because AI Mode and AI Overviews may use different models and techniques, and AI features may not trigger on every search. citeturn27view0turn27view1turn28view0

### ChatGPT / OpenAI Search Citation Evidence

OpenAI’s official ChatGPT help says search-connected ChatGPT responses **may include inline citations**, and if inline citations are not shown, users can open a **Sources** panel with cited sources and other relevant links. For Enterprise and Edu, OpenAI documents the same basic source-viewing behavior. citeturn9search1turn9search4

OpenAI also has an official developer path: its API web-search guide documents both the `web_search` tool in the Responses API and `gpt-5-search-api` in Chat Completions. The API returns cited URLs through `annotations` / `url_citation` objects, and OpenAI explicitly says that when displaying web results or information from web results to end users, **inline citations must be clearly visible and clickable**. The web search docs also show configurable approximate user location and search-context-size controls, which directly matter for reproducibility. citeturn15view0turn15view1turn14view1turn15view3

The boundary between the consumer product and the API is where people get cute and then get in trouble. OpenAI’s consumer Terms of Use say users may not **“automatically or programmatically extract data or Output.”** So, as a matter of claim safety and contractual hygiene, automated monitoring of the consumer ChatGPT UI is a bad candidate for Observatory defaults. If you want an official automation path, use the API. If you want to observe the consumer UI, do it manually and store it as manual evidence capture with its limitations. citeturn10view0

OpenAI’s Terms also say output may not always be accurate and should not be relied on as a sole source of truth. The web-search docs add another operational wrinkle: `search_context_size` does **not** guarantee a specific number of sources or citations. That means “ChatGPT cited only three sources” is not a stable cross-run metric and should not be treated like a SERP position. citeturn10view0turn15view3

Safe ChatGPT evidence for Observatory therefore includes: observed prompt text, product/API surface, model when exposed, date/time, approximate location if explicitly set, answer presence/absence, visible cited URLs/titles/domains, and provider annotations when using the API. What should not be automated by default is consumer-UI extraction. What should not be claimed is any universal statement like “ChatGPT trusts this source” or “this citation proves the source ranks in ChatGPT.” citeturn9search1turn15view0turn10view0

### Perplexity / Answer Engine Citation Evidence

Perplexity’s help center says product responses include citations and links to original sources so users can verify information. Its API stack is broad: the **Search API** returns ranked results with domain/language/region filtering; the **Sonar API** provides grounded chat completions; and the **Agent API** can use a `web_search` tool. Perplexity also publishes official guidance for parsing citations in streaming output. citeturn17search12turn16search1turn16search13turn16search5turn16search4

Perplexity is unusually explicit on API privacy/retention for at least one major surface: its privacy/security docs state a **Zero Data Retention Policy for the Sonar API**, saying Perplexity does not retain data sent via Sonar API and does not use customer data to train models. That is highly relevant for deciding what enters The Observatory from customer-driven API runs versus what should remain external. citeturn17search0

Perplexity’s APIs also expose meaningful context controls: the Search API supports domain, language, and region filtering; its search/sonar filters include date and location controls. This makes Perplexity one of the cleaner surfaces for methodology-driven observation. It is still volatile, though. The official prompt guide warns that LLMs may still answer when search results are thin or off-target rather than clearly flagging the gap. citeturn16search1turn16search3turn16search7turn16search8turn17search11turn16search12

What remains unclear in the reviewed official sources is the exact scope of storage/redistribution rights for returned answer text versus citation metadata across all Perplexity API products. The privacy docs are clear on retention for Sonar API input handling, but they are not a complete redistribution policy for harvested source content. So the safe posture is: **store your own observation metadata and citation references; treat broad answer-text redistribution and third-party content reuse as a separate legal/terms review item.** Unclear — needs confirmation. citeturn17search0turn18search0

### Bing Copilot / Microsoft AI Search Evidence

Microsoft’s public Copilot documentation says that for certain information-seeking conversations, Copilot is grounded in web search results and provides **hyperlinked citations** after generated responses. Microsoft 365 Copilot documentation similarly says users can open a **sources** button to see the Bing query and the sources used, and multiple support pages tell users to verify citations because AI can make mistakes. citeturn24search0turn24search3turn22search2turn22search18

On the developer side, the big change is that the old **Bing Search APIs were retired on August 11, 2025**, and Microsoft directs customers toward **Grounding with Bing Search** within Azure AI Agents / Foundry. Those docs describe grounding as retrieving real-time public web data or relevant chunks that the model then uses to generate a response. So Microsoft does provide an official API path for Bing-grounded AI answers, but it is not the same thing as a public “Bing Copilot consumer answer API.” citeturn21search2turn23search0turn23search2

For site owners, Microsoft introduced **AI Performance** in Bing Webmaster Tools public preview. Microsoft says it reports when a site is cited in AI-generated answers across Microsoft Copilot, AI-generated summaries in Bing, and select partner integrations; the help page says the report contains information about a site’s AI performance on Microsoft Copilots and partner surfaces. The official blog is careful to describe total citations, average cited pages, and grounding queries as visibility indicators, not authority or ranking facts, and the later June 2026 expansion says new capabilities like citation share are preview features built on continuously advancing AI/ML systems and aggregated citation signals. That is exactly the kind of “provider testimony, not fact” language The Observatory should respect. citeturn25search1turn25search2turn25search4

The Bing Webmaster API documentation reviewed here covers search/index/crawl data for registered sites, but it does not document an AI Performance endpoint. So the right stance is: **Bing Webmaster Tools has owner-facing AI citation reporting; an official API export path for that reporting was not found in the reviewed docs.** Unclear — needs confirmation. citeturn21search6turn25search1turn25search2

### Gemini / Google AI Product Citation Evidence

Gemini should be treated as a separate witness from Google Search. The Gemini API supports **grounding with Google Search**, which Google says connects the model to real-time web content so Gemini can provide more accurate answers and **cite verifiable sources** beyond its knowledge cutoff. That is not the same product surface as Google AI Overviews or AI Mode, even if both use Google models and web data. citeturn26search8turn26search0

In the Gemini app/help materials, Google documents that when Gemini Apps directly quote large amounts of text from a webpage, users will see a link to that webpage in the sources list, and web images show source links as well. That means consumer-app source behavior is present, but it is conditional and not guaranteed for every answer in the same way a search-first product like Perplexity frames citations. citeturn26search2

The Gemini API additional terms matter here. Google says the Gemini API is for developers building with Google AI models for professional or business purposes; use is region-limited; and archived terms note that applicable law may require attribution to users when generated content is returned as part of an API call. So storage and display rules should be tied to exact API plan/region/contract terms, not hand-wavy “it’s just AI output” assumptions. citeturn26search3turn26search11

Safe Observatory treatment: manual or API-based Gemini observations are admissible when provenance is captured and the source links/citation metadata are preserved. Unsafe treatment: conflating Gemini app citations with Google Search AI Overviews, or assuming that a grounded Gemini answer proves what Google Search would show. These are different instruments. Same solar system, different telescope. citeturn26search8turn27view0

### DataForSEO AI / GEO Coverage

DataForSEO now has meaningful AI/GEO coverage, but its capabilities span **different evidence classes** and should not be merged into one bucket. Officially documented capabilities include **Google AI Mode SERP API**, **Google Organic SERP API with AI Overview loading parameters**, **AI Optimization API**, **LLM Responses API**, **LLM Mentions API**, and **ChatGPT LLM Scraper API**. DataForSEO also publishes an AI Visibility Tracker product. citeturn4view2turn3search1turn4view0turn7view0turn7view2turn7view1turn3search16

The cleanest facts:

- **Google AI Mode SERP** is officially documented and priced as a SERP API product. DataForSEO says it emulates specified location/search-engine context and returns AI Mode results for specified keyword/language/location. citeturn4view2turn4view1
- **Google AI Overviews** are available **indirectly** through Google Organic SERP capture using a `load_async_ai_overview` parameter, and DataForSEO’s help center/blog explicitly says AI Overviews can be tracked with its Google Organic SERP API. citeturn3search1turn2search22
- **LLM Responses API** officially supports ChatGPT, Claude, Gemini, and Perplexity, and allows choosing specific model versions for testing. citeturn7view0
- **LLM Mentions API** is an estimate/aggregate layer: it provides keyword/brand/website mentions and metrics like AI search volume, impressions, and mention count. That is not the same thing as individual direct observations. citeturn7view2
- **ChatGPT LLM Scraper** is explicitly described by DataForSEO as providing structured results from **scraped ChatGPT searches** and returning fields for sources the model actually cited or relied on in the final answer, including title, snippet, domain, URL, source name, publication date, and other UI elements. citeturn7view1turn8view4turn8view2

DataForSEO’s results-storage and usage rules matter. Standard-method results are stored for 30 days, Live-method results are not stored, HTML results are stored for 7 days, and SERP JSON results are stored for 30 days. Its Terms also say SERP data/content obtained through the Service must not be used to compete with or adversely affect the business interests of the originating search-engine providers, and customers are responsible for use that violates upstream provider terms or legal rights. That means DataForSEO is not a magical indemnity cloak. It is a provider, not holy water. citeturn4view3turn5view0

| DataForSEO Capability | Surface | Fields Returned | Pricing Unit | Rights/Retention Notes | Classification | Source |
| --- | --- | --- | --- | --- | --- | --- |
| Google AI Mode SERP API | Google AI Mode | SERP results for keyword/language/location; HTML and advanced endpoints; check URL for verification citeturn4view2 | Per SERP page; Standard $0.0012, Priority $0.0024, Live $0.004 citeturn4view1 | Standard JSON stored 30 days; Live not stored; HTML 7 days; usage subject to DataForSEO terms citeturn4view3turn5view0 | Available and documented | citeturn4view2turn4view1 |
| Google AI Overview capture via Organic SERP | Google Search AI Overviews | Organic SERP with `load_async_ai_overview` support citeturn3search1 | Per SERP/API pricing page applicable | Same DataForSEO storage/terms envelope citeturn4view3turn5view0 | Available indirectly through SERP feature capture | citeturn3search1turn2search22 |
| LLM Responses API | ChatGPT, Claude, Gemini, Perplexity | Structured LLM responses; model versions selectable citeturn7view0 | Task-based; pricing calculator referenced by DataForSEO citeturn7view0 | Provider-generated/model-mediated output, not direct UI truth | Available and documented | citeturn7view0 |
| ChatGPT LLM Scraper API | ChatGPT Search | Structured scraped ChatGPT search results including cited sources, URLs, domains, titles, snippets, publication dates, and UI elements citeturn7view1turn8view4turn8view2 | Task-based | Explicitly scraper-based; upstream ToS/legal review required citeturn7view1turn10view0 | Available and documented, but risky | citeturn7view1turn8view4 |
| LLM Mentions API | Multi-LLM mention layer | Mentions, sources, AI search volume, impressions, mentions count citeturn7view2 | Live/task pricing | Aggregated/provider-normalized metrics, not direct observation | Available and documented | citeturn7view2 |
| AI Keyword Data API | Multi-LLM keyword layer | AI search volume estimates and trend data citeturn4view0 | API pricing | Estimate layer, not citation observation | Available and documented | citeturn4view0 |
| AI Visibility Tracker | Multi-model | Weekly LLM-mention benchmarking across business categories citeturn3search16 | Free public tracker product | Provider testimony, benchmark abstraction | Available but score-like/provider-normalized | citeturn3search16 |

## Tooling Market

### Third-Party GEO / AI Visibility Tools

The third-party market is real and growing, but most products blend at least three things: direct prompt/citation observation, provider-normalized aggregation, and proprietary scoring. That is fine commercially. It is poison if you store it as ground truth. Observatory can store these outputs only as **provider testimony** with provenance, methodology label, and caveats. citeturn34search20turn35search0turn35search5turn36search4

Profound says it runs structured prompts across AI platforms daily and tracks where/how a brand appears, including citations, sentiment, ranking, and competitive presence. That makes it a mix of direct observation and proprietary normalization. Public pricing visibility is limited now, with the pricing page emphasizing customized plans while still describing methodology. citeturn34search20turn34search0

Peec AI positions itself as AI search analytics for marketing teams across ChatGPT, Perplexity, and Gemini, with competitor benchmarking and citation insight. Public methodology detail is thinner than the sales copy. That means the product category is clear, while the measurement internals remain partly opaque. Unclear — needs confirmation. citeturn34search5

Otterly.ai explicitly tracks brand mentions and website citations across ChatGPT, Perplexity, and Google AI Overviews, and its own documentation/blog expands that list to Gemini, Claude, Copilot, and AI Mode coverage. Its pricing is transparent, starting at $29/month. This is a lower-barrier monitoring layer, but still a provider-managed observation system rather than first-party platform truth. citeturn34search2turn34search6turn34search10

AthenaHQ positions itself as an AI visibility/action platform with public pricing and claims to track and improve AI search visibility. The official public pricing page is accessible; detailed methodology remains product-marketing heavy. Treat outputs as provider-normalized observations unless and until a more rigorous methodology document is reviewed. citeturn34search3turn34search15

Semrush’s AI Visibility Toolkit is explicit about its pricing and feature set: AI visibility reports, mentions/citations/opportunities, prompt tracking, AI share of voice/sentiment, and related AI-search checks. That is useful, but still not first-party platform fact. It is Semrush’s measurement layer. citeturn35search0turn35search4turn35search16

Ahrefs Brand Radar is one of the clearest examples of a normalized measurement product. Ahrefs says it tracks AI visibility across **405M+ search-backed prompts** and lets users benchmark share of voice, mentions, citations, and top cited domains/pages. That is not direct full-web truth; it is a modeled/search-backed sample frame. Useful, but not universal. citeturn35search1turn35search5turn35search9

Rankscale, Scrunch, ZipTie, Nozzle, and Goodie illustrate the rest of the market spectrum: broader engine coverage, more prompt scheduling, more optimization guidance, more shopping/agent-specific visibility, or more SERP/AIO-focused tracking. Their public pages confirm product existence and certain features, but methodology precision varies widely. Where the product emphasizes “visibility scores,” “share of answer,” or similar roll-ups, store those only as vendor-generated metrics. citeturn36search4turn36search0turn35search3turn35search19turn36search2turn36search6turn35search2turn36search1

| Tool | Surfaces Claimed | Main Outputs | API or Export Clarity | Pricing Clarity | Metric Class | Strongest Use | Weakest Use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Profound | Multi-AI platforms | citations, ranking, sentiment, competitive presence citeturn34search20 | Export/API unclear in reviewed public docs | Low public clarity | Direct observation + provider-normalized + proprietary score | Enterprise multi-surface monitoring | Treating its metrics as platform facts |
| Peec AI | ChatGPT, Perplexity, Gemini, others in marketing copy citeturn34search5 | visibility, benchmarking, citations | Unclear — needs confirmation | Unclear publicly | Provider-normalized observation / unknown | Marketing-team visibility overview | Methodology transparency |
| Otterly | ChatGPT, Perplexity, Google AIO; blog adds Gemini/Claude/Copilot/AI Mode citeturn34search2turn34search10 | mentions, citations, prompt monitoring | Export/API unclear in reviewed public docs | Clear: from $29/mo citeturn34search6 | Direct observation + provider-normalized | Low-friction prompt/citation tracking | Formal enterprise methodology |
| AthenaHQ | Multi-AI search surfaces citeturn34search3turn34search15 | visibility tracking + action layer | Unclear | Clear-ish public pricing | Provider-normalized / proprietary | Workflow/action-oriented teams | Pure evidence archive use |
| Semrush AI Visibility Toolkit | AI visibility surfaces + prompt tracking citeturn35search16 | mentions, citations, share of voice, opportunities | Export exists; API not clearly documented in reviewed source | Clear: from $99/mo citeturn35search0turn35search4 | Provider-normalized + proprietary | Broad SEO-adjacent operations | Courtroom-grade evidence claims |
| Ahrefs Brand Radar | AI search across huge search-backed prompt dataset citeturn35search5 | mentions, citations, share of voice, cited domains/pages | Product export likely, API unclear in reviewed source | Clear: from $199/mo citeturn35search9 | Provider-normalized + proprietary | Large-scale benchmark/trend analysis | Exact individual-answer archiving |
| Rankscale | 17+ engines incl. ChatGPT, Perplexity, Gemini, Claude, Copilot, AIO, AI Mode citeturn36search4 | visibility score, citations analysis, shopping/source-box analysis citeturn36search0 | Custom API mentioned for tailored plans citeturn36search0 | Clear-ish | Direct observation + provider score | Broad engine coverage | Separating observation from recommendation |
| Scrunch | ChatGPT, Claude, Gemini, Perplexity, Google AIO citeturn35search19 | share of answer, citations, sentiment, placement | Enterprise Data API documented citeturn35search11 | Starts at $250/mo citeturn35search7 | Direct observation + provider-normalized | Enterprise monitoring at scale | Using platform sentiment as fact |
| Nozzle | Google SERP / AI Overviews focus citeturn35search2turn35search18 | AIO/ SERP feature tracking | Exports to BI tools mentioned generally citeturn35search10 | Unclear in reviewed source | Public surface capture | SERP-centric AIO tracking | Cross-LLM answer-engine visibility |
| Goodie | AI shopping/agentic commerce surfaces citeturn36search1 | product visibility in AI shopping experiences | Unclear | Public pricing not clear in official source reviewed | Provider-normalized / unknown | Commerce-specific monitoring | General AI citation visibility |

## Evidence Boundary

### Public vs Private AI Evidence Boundary

The cleanest line is this: **public external observations** are candidates for Observatory; **customer-private, account-personalized, or contract-sensitive operational data** should stay out unless there is a later explicit owner ruling and a scoped overlay model. Google, Microsoft, OpenAI, Anthropic, and Perplexity all document some degree of personalization, history, or connected-data behavior in at least parts of their ecosystems, which means not every answer surface is a public witness by default. citeturn24search9turn9search16turn30search8turn22search10

Manual screenshots or hashes of public AI answers are strong candidates if captured with timestamp and context metadata. Provider/API-returned citation/source metadata is also a strong candidate where the API is official. Third-party scores should be admissible only if labeled as vendor methodology outputs. Customer prompt logs, connected-app answers, private analytics, and account-specific histories belong outside the Observatory core unless intentionally handled in a separate customer-authorized layer. citeturn15view0turn17search0turn22search15turn30search10

| Category | Store in Observatory Now | Later Possible | Belongs in SearchClarity or Customer Layer | Notes |
| --- | ---: | ---: | ---: | --- |
| Public AI answer observation | Yes | Yes | Sometimes mirrored | Requires prompt/context/time caveat |
| Public AI citation/source observation | Yes | Yes | Sometimes mirrored | Best early candidate evidence |
| Public Google AI Overview SERP observation | Yes | Yes | Sometimes mirrored | Manual or approved-provider capture only |
| Manual AI answer screenshot/hash | Yes | Yes | Sometimes mirrored | Strong provenance aid |
| Provider/API-returned AI answer data | Yes, if official API and terms-compliant | Yes | Sometimes | Keep request/response metadata |
| Provider/API-returned citation/source data | Yes | Yes | Sometimes | Best machine-readable evidence |
| Third-party AI visibility score | Yes, as provider testimony only | Yes | Sometimes | Never as fact |
| Account-personalized AI answer | No by default | Maybe with strict overlay | Yes | High privacy/variance risk |
| Customer/private prompt logs | No by default | Maybe with explicit authorization | Yes | Private data boundary |
| Customer/private site analytics | No | Possibly in customer layer only | Yes | Not Observatory-core evidence |
| Owner-internal AI visibility tests | No in shared Observatory core | Maybe in internal overlay | Yes | Keep separate from public corpus |
| Derived claims / interpretations | No as stored fact | Read-time only preferred | Yes | LLM does the astronomy later |

### Volatility, Reproducibility, and Same Prompt / Same Context Rule

The academic and official evidence is blunt: reproducibility is weak. Google says AI Mode and AI Overviews may use different models and techniques and vary in links shown; Microsoft says repeated prompts can produce different Copilot responses; OpenAI says output is probabilistic and may be inaccurate; a 2026 measurement paper shows substantial variability across repeated samples even for identical queries; and a 2025 *Nature Communications* paper shows cited sources often do not fully support generated claims. citeturn27view0turn24search4turn10view0turn38view1turn38view0

That means The Observatory needs a **same prompt / same context** rule. Minimum metadata to preserve observation meaning: exact prompt/query text, surface/provider, product/model/version if exposed, login/account state if known, location/region, language, device/interface, timestamp, answer presence/absence, and exact citation/source set shown or returned. If any of those are missing, the evidence is still usable, but weaker and less comparable. citeturn14view1turn27view1turn24search3turn16search1turn26search8turn30search0

Required caveat language should be standardized and repeated relentlessly, because reality is rude and will not adapt itself to your dashboard. Recommended caveat: **“This AI citation observation is prompt/context/time-bound and may not reproduce exactly.”** That is not lawyerly filler. It is the scientific minimum. citeturn38view1turn38view2turn38view3

### Recommended Observatory Handling

Best early candidates are the surfaces with a combination of visible citations and official capture paths: **Google Search Console gen-AI reporting, Bing Webmaster Tools AI Performance, OpenAI web-search API annotations, Perplexity APIs, Gemini grounding responses, Anthropic web-search tool responses, Azure Grounding with Bing Search, and Google AI Overviews/AI Mode or Bing/Copilot public captures done manually or through officially contracted providers where terms are tolerable.** citeturn27view2turn25search1turn15view0turn16search1turn26search8turn30search0turn23search0

Evidence that belongs only in a customer-layer or explicit overlay includes connected-app answers, personalized answer histories, internal experiments tied to private business context, and customer analytics. Evidence that should be avoided in early Observatory scope includes consumer-UI scraping where terms prohibit extraction, storing proprietary visibility scores as if they were facts, and storing broad answer text when the terms or copyright/reuse posture is unclear. citeturn10view0turn17search0turn26search3

Provider/tool estimates can be stored, but only in a labeled class such as **provider testimony** or **proprietary score output**. M1 research gates should therefore focus on: official API terms and reuse boundaries, official product/UI automation restrictions, whether manual screenshot/hash capture is sufficient for provenance, and whether each admitted surface can be normalized into a non-interpretive observation envelope. citeturn10view0turn5view0turn17search0turn26search3

## Claim Safety and Provenance

### Evidence and Provenance Fit

The Observatory’s evidence requirements are broadly achievable for grounded APIs and somewhat patchier for consumer-product UIs. Official APIs from OpenAI, Perplexity, Gemini, Anthropic, Azure Bing grounding, and DataForSEO are stronger on machine-readable provenance. Google AI Overviews/AI Mode and Bing/Copilot public UIs are stronger on public relevance, weaker on reproducible structured capture unless using owner telemetry or approved providers. Third-party tools are useful for discovery and benchmarking, but they degrade provenance if treated as direct truth rather than derived vendor datasets. citeturn15view0turn16search1turn26search8turn30search0turn23search0turn4view2turn25search1

| Evidence Need | Google AIO | ChatGPT Search | Perplexity | Bing Copilot | Gemini | DataForSEO | Third-Party Tools | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Surface/provider name | Strong | Strong | Strong | Strong | Strong | Strong | Strong | Usually easy |
| Product/model/version if available | Weak in public UI | Medium to strong in API | Medium to strong in API | Weak in public UI, stronger in Azure | Medium in API | Medium to strong | Weak to medium | Often absent in consumer UIs |
| Query/prompt wording | Manual capture needed | Strong | Strong | Manual capture needed | Strong | Strong | Strong | Must preserve exact text |
| Location/language/device/account state | Manual or inferred | Strong in API | Strong in API | Manual/partial | Strong in API | Strong | Varies | Critical for reproducibility |
| Capture timestamp | Strong if you record it | Strong | Strong | Strong if you record it | Strong | Strong | Strong | Non-negotiable |
| Answer presence/absence | Strong | Strong | Strong | Strong | Strong | Strong | Strong | Easy, but still context-bound |
| Answer text if allowed | UI-dependent | Usually yes via API | Usually yes via API | UI-dependent | Usually yes via API | Yes by endpoint | Usually yes | Reuse rights vary |
| Citation/source URLs/domains | Visible in UI | Strong via annotations | Strong | Visible in UI | Strong when grounded | Strong on supported endpoints | Usually strong | Core evidence item |
| Screenshot/hash | Manual | Manual or generated | Manual or generated | Manual | Manual or generated | Varies | Varies | Excellent provenance supplement |
| API request/response metadata | No public API found | Strong | Strong | Strong via Azure tooling | Strong | Strong | Weak to medium | Best for machine evidence |
| Public/private classification | Public | Mixed | Mixed | Mixed | Mixed | Provider | Provider | Needs explicit label |
| Rights/retention classification | Medium | Stronger in API than UI | Medium | Medium | Medium | Strong within DFS envelope | Weak to medium | Often needs legal pass |
| Volatility caveat | Required | Required | Required | Required | Required | Required | Required | No exceptions |

### Safe and Unsafe Claim Language

Safe wording should always say **what was observed, where, when, and under what context**. Unsafe wording turns an observation into a universal truth, ranking statement, trust judgment, or causal theory.

| Evidence | Safe Wording | Unsafe Wording | Required Caveat |
| --- | --- | --- | --- |
| AI Overview source URL | For query X, Google displayed an AI Overview in observed context C on date T, and URL/domain Z appeared among the displayed supporting links. | Google considers Z authoritative for X. | Prompt/context/time-bound; may vary by user/query/device/region. |
| ChatGPT citation | For prompt X, ChatGPT search returned an answer on date T that cited/source-linked URL Z. | ChatGPT trusts Z. | Product/API/config-bound; citations may differ across runs. |
| Perplexity citation | For prompt X, Perplexity returned an answer on date T that cited URL Z. | Perplexity ranks Z as the best source in general. | Context-bound; answer composition may vary. |
| Bing/Copilot source | In observed Copilot/Bing response X on date T, source URL Z appeared in the cited source set. | Microsoft endorses Z. | AI-generated answers can make mistakes; verify sources. |
| Gemini citation | For grounded Gemini response X on date T, Google Search-grounding metadata/source links included URL Z. | Gemini proves Z is Google Search’s top answer. | Gemini grounding is a separate product surface from Google Search. |
| Third-party AI visibility score | Vendor V reported score S under its own methodology for prompt set P/time range T. | The brand has S% AI visibility. | Provider testimony only; score depends on vendor sampling/model. |
| Brand mention | In observed answer X, brand B was mentioned. | AI prefers brand B. | Mention ≠ recommendation or authority. |
| Answer inclusion | Surface Y returned an answer for prompt X at time T. | Surface Y always answers this topic. | Presence can vary across runs and contexts. |
| Answer absence | In observed prompt/context X, surface Y did not cite or mention target Z. | Surface Y never cites Z. | Absence in one run is not universal absence. |

## Decision Inputs and Appendices

### Questions / Unknowns To Confirm

Several important items remain unresolved enough that they should be marked with a big yellow sticky note, not guessed through:

- **Google public live-capture API for AI Overviews / AI Mode:** no such API was found in the reviewed official Google Search docs, but a broader legal/product review should confirm whether any Google-approved partner paths exist beyond Search Console and public UI/manual capture. citeturn27view0turn27view2
- **Bing Webmaster API support for AI Performance:** owner-facing AI Performance exists, but no official API endpoint was found in the reviewed docs. Unclear — needs confirmation. citeturn25search1turn25search2turn21search6
- **Perplexity redistribution rights for full answer text and downstream storage policies across all API products:** privacy/retention are documented for Sonar, but redistribution rules need a contract-level read. Unclear — needs confirmation. citeturn17search0turn18search0
- **Vendor methodology details for several third-party GEO tools:** many products clearly exist, but their exact scoring logic, export rights, and normalization methods are not fully public. Unclear — needs confirmation. citeturn34search5turn35search3turn36search1

### Decision Inputs For M1 Roadmap

Before M1 roadmap sequencing, the must-knows are: which surfaces can be observed via official APIs; which surfaces can be admitted via manual capture only; which surfaces expose owner telemetry; and which ones create avoidable contract or privacy risk if automated. That points to a phased order: official APIs first, owner telemetry second, public manual capture third, third-party-vendor testimony last. citeturn15view0turn27view2turn25search1turn10view0

Before schema, the must-knows are: required provenance fields, rights classification, retention limits, and whether answer text itself is necessary or whether storing citation/source metadata plus screenshot/hash is sufficient. The current evidence says those fields should exist before any schema debate about cleverness. Cleverness can wait outside. It has enough hobbies already. citeturn4view3turn17search0turn26search3turn38view1

Before AI/GEO source admission, the must-knows are: official terms on automation, whether the source is public or account-personalized, whether its outputs are reproducible enough to compare, and whether the source’s own metrics are direct observations or proprietary estimates. Before the first customer-facing report, the must-knows are: standardized caveat language, claim-safety templates, and explicit labeling of vendor scores as vendor scores. Before any automation, the must-knows are: exact permitted path, request rates, retention periods, and whether upstream provider terms create conflict. citeturn10view0turn5view0turn27view2turn25search4

### Decision-ready Summary

Recommended status by source:

- **Google AI Overviews / AI Mode public observations:** safe candidate for public observation **via manual capture or compliant provider path**, not as universal truth. citeturn27view0turn27view1turn28view0
- **Google Search Console generative AI report:** allowed through official provider/owner telemetry; strong candidate. citeturn27view2turn29search3
- **ChatGPT consumer UI:** risky / avoid automation; manual evidence only by default because OpenAI prohibits automatic extraction from the consumer service. citeturn10view0
- **OpenAI web-search API:** safe candidate through official API/provider. citeturn15view0turn15view1
- **Perplexity APIs:** safe candidate through official API/provider, subject to terms review for storage/redistribution nuances. citeturn16search1turn16search13turn17search0
- **Bing/Copilot public UI:** safe candidate for public observation manually; risky to automate consumer UI without explicit allowance. citeturn24search0turn24search3
- **Azure Grounding with Bing Search:** safe candidate through official API/provider. citeturn23search0turn23search2
- **Bing Webmaster Tools AI Performance:** allowed through official provider/owner telemetry. citeturn25search1turn25search2
- **Gemini grounded API responses:** safe candidate through official API/provider. citeturn26search8turn26search0
- **Gemini consumer-app answers:** manual public observation candidate; do not conflate with Google Search. citeturn26search2
- **Claude web-search API/tool:** safe candidate through official API/provider. citeturn30search0turn30search1
- **DataForSEO Google AI Mode / AIO capture:** allowed only through official DataForSEO provider relationship, but classify carefully as provider-mediated observation. citeturn4view2turn3search1
- **DataForSEO ChatGPT LLM Scraper:** risky / avoid default admission unless explicit legal review says yes; it is scraper-based and collides with OpenAI consumer extraction restrictions. citeturn7view1turn10view0
- **Third-party GEO tool scores:** allowed only as provider-testimony overlays, not Observatory facts. citeturn35search0turn35search5turn36search4
- **Customer/private prompt logs, connected-data answers, private analytics:** allowed only through customer-layer/read-time overlay or explicit authorization; not Observatory core. citeturn22search15turn30search10turn9search16

Must know before M1 roadmap sequencing: official API/terms status for each candidate surface; minimum provenance package; whether screenshot/hash is enough for evidence preservation; and which owner-telemetry sources are mature enough to prioritize. citeturn27view2turn25search1turn15view0

Must know before schema: evidence object boundaries, rights/retention classes, and strict distinction between direct observation, provider-normalized observation, proprietary estimate, and derived interpretation. citeturn4view3turn7view2turn35search5

Must know before AI/GEO source admission: whether the source is public, whether automation is allowed, whether citations are visible/returnable, and whether outputs are sufficiently provenance-complete to archive. citeturn10view0turn27view0turn30search0

Must know before first AI/GEO customer-facing report: claim-safe language, reproducibility caveats, and how vendor scores will be labeled so nobody mistakes “tool says X” for “reality says X.” citeturn38view1turn38view0turn25search4

Must know before any automation: exact terms, retention windows, export rights, and whether the chosen mechanism is an official API, owner-telemetry export, manual capture support path, or a scraping workaround in a cheap mustache. The last one should not ship. citeturn10view0turn4view3turn5view0

### Appendix A — Surface Comparison Table

| Surface | Official Fact Pattern | Best Evidence Type | Biggest Risk |
| --- | --- | --- | --- |
| Google AI Overviews | Public Search feature with supporting links; no extra SEO requirements; Search Console reporting now exists citeturn27view0turn27view2 | Manual/public capture + Search Console telemetry | Variability and no reviewed public live-capture API |
| Google AI Mode | Public AI search mode with helpful web links and follow-ups; Search Console reporting now exists citeturn27view1turn27view2 | Manual/public capture + Search Console telemetry | Query fan-out/context drift |
| ChatGPT Search | Inline citations/Sources panel; official API web search exists citeturn9search1turn15view0 | Official API annotations | Consumer UI extraction prohibited |
| Perplexity | Citation-first answer engine; official APIs | Official API response + citation metadata | Storage/redistribution nuance needs confirmation |
| Bing/Copilot | Grounded answer mode with citations; Bing Webmaster AI Performance | Manual capture + owner telemetry + Azure grounding | Public UI automation risk; API fragmentation |
| Gemini | Grounded API with citations; app sources conditional | Official grounded API metadata | Confusing Gemini with Google Search |
| Claude | Web search tool with citations | Official API/tool output | Same volatility as other answer engines |
| DataForSEO | Mixed direct capture, scraper capture, and estimate layers | Contracted provider data with explicit classification | Upstream terms conflict and score confusion |

### Appendix B — Evidence Category Boundary Table

| Category | Boundary Decision | Reason |
| --- | --- | --- |
| Public citation URL/domain | Admit | High-value, low-interpretation evidence |
| Public answer text | Admit cautiously | Rights/reuse review may differ by provider |
| Screenshot/hash | Admit | Provenance anchor |
| Provider annotation metadata | Admit | Machine-readable evidence |
| Third-party share-of-voice score | Admit as testimony only | Proprietary and sample-bound |
| Customer prompt logs | Exclude by default | Private and context-sensitive |
| Connected-app answer history | Exclude by default | Personalized/private |
| Customer analytics | Exclude from core | Customer-layer data, not public observation |
| Derived recommendation | Keep out of stored fact layer | Read-time interpretation belongs to LLM |

### Appendix C — Third-Party GEO Tool Table

| Tool | Store Raw Outputs? | Store Scores? | How to Label |
| --- | --- | --- | --- |
| Profound | Yes, if contract allows and provenance retained | Yes | “Profound-reported metric” |
| Peec AI | Yes, if contract allows | Yes | “Peec-reported metric” |
| Otterly | Yes | Yes | “Otterly observation / metric” |
| AthenaHQ | Yes | Yes | “Athena-reported metric” |
| Semrush | Yes | Yes | “Semrush-reported AI visibility metric” |
| Ahrefs Brand Radar | Yes | Yes | “Ahrefs modeled AI visibility metric” |
| Rankscale | Yes | Yes | “Rankscale-reported visibility score” |
| Scrunch | Yes | Yes | “Scrunch-reported monitoring metric” |
| Nozzle | Yes | Limited score usage | “Nozzle SERP/AIO observation” |

### Appendix D — Safe vs Unsafe Claim Matrix

| Pattern | Safe | Unsafe |
| --- | --- | --- |
| Citation observed | “Surface Y cited URL Z for prompt X at time T.” | “Surface Y endorses URL Z.” |
| Mention observed | “Brand B was mentioned in observed answer X.” | “Brand B leads AI search.” |
| No citation observed | “Target Z did not appear in this observed run.” | “Target Z is never cited.” |
| Vendor score | “Vendor V reported score S under its methodology.” | “Score S is the brand’s true AI visibility.” |
| Search Console / Webmaster telemetry | “Owner-facing report showed N impressions/citations in provider report.” | “Provider ranked the site as authoritative.” |