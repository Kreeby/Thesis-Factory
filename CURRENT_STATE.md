# Current Project State

Last updated: 2026-09-23

## Current Phase

**Phase 1 — Topic Researchability**

Phase 0 — Project Foundation — is complete.

The project now has operational capabilities for:

* bounded scholarly literature planning;
* scholarly discovery;
* bibliographic verification;
* abstract-level relevance assessment;
* source-text resolution;
* immutable artifact acquisition;
* deterministic scholarly-document normalization;
* exact evidence addressing and verification.

The project is now moving from verifiable normalized evidence toward retrieval over scholarly documents.

---

## Current Objective

Extend the Topic Researchability workflow from addressable scholarly evidence toward deterministic and measurable passage retrieval.

The current focus is:

**paragraph-level retrieval over normalized scholarly documents.**

The system can already identify and verify an exact character span inside a normalized scholarly paragraph.

The next capability must transform normalized paragraphs into retrieval units without weakening provenance or introducing unnecessary chunking heuristics.

The initial retrieval design is:

`one normalized paragraph = one retrieval unit`

with section and source metadata preserved alongside the paragraph.

Chunk splitting, paragraph merging, semantic embeddings, vector storage, and contextual expansion are intentionally deferred until retrieval behaviour is measured empirically.

---

## Completed

### Project Foundation

* GitHub repository created and `main` initialised.
* Canonical project documentation established.
* `PROJECT.md` created.
* `AGENTS.md` created.
* `ARCHITECTURE.md` created.
* `CURRENT_STATE.md` established as the operational project-state artifact.
* ADR process established under `docs/decisions/`.
* ADR-0001 accepted: Claude is the default LLM family for autonomous reasoning agents.
* Repository established as the canonical source of project truth.
* Branch → pull request → human review → merge established as the default development workflow.
* Pull requests targeting `main` are required to modify `CURRENT_STATE.md`.
* A GitHub Actions Current State Gate enforces the `CURRENT_STATE.md` update invariant.

### Phase 1 — Scholarly Discovery and Verification

* Python 3.12 project runtime established using `uv`.
* `SourceRecord` domain model implemented with runtime validation.
* OpenAlex scholarly discovery integration implemented.
* OpenAlex metadata is normalized into internal `SourceRecord` artifacts.
* OpenAlex abstract inverted indexes are reconstructed into plain-text abstracts when available.
* Crossref DOI metadata lookup integration implemented.
* DataCite DOI metadata lookup integration implemented.
* Crossref and DataCite are composed behind a provider-independent DOI registry boundary.
* Bibliographic metadata comparison implemented.
* Source identity verification implemented with explicit:

  * `CONFIRMED`;
  * `CONFLICTING`;
  * `INSUFFICIENT_DATA`.
* Verification discrepancies are preserved rather than hidden.
* Source verification can operate independently on an already discovered source.
* `discover_and_verify_sources` workflow implemented.
* DataCite fallback was verified against an arXiv DOI not resolved through Crossref.

### Phase 1 — LLM Reasoning Boundary

* Provider-independent structured LLM reasoning boundary implemented.
* Anthropic / Claude structured reasoning adapter implemented.
* Claude-backed scholarly source relevance assessment implemented.
* Relevance assessment uses explicit:

  * `RELEVANT`;
  * `NOT_RELEVANT`;
  * `UNCERTAIN`;
  * `INSUFFICIENT_EVIDENCE`.
* Sources without sufficient textual evidence terminate deterministically as `INSUFFICIENT_EVIDENCE`.
* Relevance behaviour is covered by deterministic tests.
* A curated relevance evaluation harness using real Claude calls has been implemented.

### Phase 1 — Literature Search Planning

* Bounded `LiteratureSearchPlanner` implemented.
* Search planning is explicitly separated from final thesis research-question formulation.
* Search plans are limited to at most five complementary scholarly search tasks.
* Search-planning output is operational metadata and is not treated as research evidence.
* Topic-level literature assessment workflow implemented.
* Results from multiple planned searches are aggregated before downstream processing.
* Duplicate scholarly sources are removed before bibliographic verification and relevance assessment.
* Search-query provenance is preserved for each discovered source.
* OpenAlex lexical and semantic search modes implemented explicitly.
* Live diagnostics demonstrated substantially better topical precision from OpenAlex semantic retrieval than lexical retrieval for the current candidate topic.
* Planner-driven literature discovery currently uses OpenAlex semantic search.
* OpenAlex semantic-search rate limiting is handled within the provider integration boundary.
* Crossref abstracts can act as fallback textual evidence when OpenAlex does not expose an abstract.
* The exact `SourceRecord` supplied to relevance assessment is preserved as `relevance_source`.

### Phase 1 — Real Literature Workflow Validation

The complete bounded discovery and relevance workflow has been executed against real scholarly providers and Claude.

For the candidate topic:

`machine learning credit risk`

a five-query run with five results per query produced:

* 25 unique scholarly sources;
* 14 `RELEVANT`;
* 0 `NOT_RELEVANT`;
* 0 `UNCERTAIN`;
* 9 `INSUFFICIENT_EVIDENCE`;
* 2 sources that could not proceed to relevance assessment because bibliographic verification could not be completed.

This demonstrated that textual evidence availability was a more material bottleneck than initial semantic retrieval precision.

### Phase 1 — Source-Text Resolution

* `SourceTextLocation` introduced as a domain artifact distinct from bibliographic `SourceRecord`.
* Bibliographic source identity and retrievable textual representations are modelled separately.
* OpenAlex full-text location lookup implemented.
* OpenAlex `best_oa_location` support implemented.
* Complete OpenAlex `locations` inspection implemented.
* OpenAlex cached full-text `content_urls` support implemented.
* Supported text-location representations include:

  * OpenAlex GROBID XML;
  * OpenAlex cached PDF;
  * original open-access PDF;
  * scholarly landing page.
* Multiple text locations for the same source are deduplicated.
* Landing pages are distinguished from directly downloadable full-text artifacts.
* Preferred text-location selection implemented.
* Preferred order is:

  1. OpenAlex GROBID XML;
  2. OpenAlex cached PDF;
  3. original open-access PDF.
* Landing pages are not treated as downloadable full text.

A real source-text coverage diagnostic over nine sources previously terminating without abstract-level evidence found:

* 9 sources lacking abstract-level evidence;
* 2 with OpenAlex GROBID XML;
* 2 with OpenAlex cached PDF;
* 3 with original open-access PDF locations;
* 3 with landing-page locations;
* 5 with no usable text location through the current OpenAlex resolver.

Inspecting all OpenAlex locations rather than only `best_oa_location` did not improve coverage for the sample.

Incomplete full-text coverage is therefore treated as an explicit supported state rather than as a trigger for unbounded provider searching.

### Phase 1 — Artifact Acquisition

* Deterministic artifact fetching implemented.
* Direct full-text locations can be downloaded independently of reasoning agents.
* Supported downloaded artifact formats currently include:

  * GROBID XML;
  * PDF.
* Downloaded artifacts are validated against their expected representation.
* HTML or access-denied responses masquerading as PDF are rejected.
* Empty artifacts are rejected.
* Maximum artifact size is bounded.
* Downloaded artifact bytes receive deterministic SHA-256 identity.
* Artifact metadata preserves the source-text location used for retrieval.
* Provider credentials are not stored in provenance artifacts.

A live authenticated OpenAlex GROBID download was successfully executed for:

`Corporate default forecasting with machine learning`

OpenAlex work:

`W3010059221`

The downloaded artifact had:

* format: `GROBID_XML`;
* size: `234692` bytes;
* content type: `application/xml; charset=utf-8`;
* SHA-256: `ae21bed28e5f9ab69878493e474bb41537621bebe692018944ed1cc2311d1d67`.

### Phase 1 — Scholarly Document Normalization

* `NormalizedDocument` implemented.
* `NormalizedSection` implemented.
* `NormalizedParagraph` implemented.
* Normalized documents preserve:

  * originating artifact SHA-256;
  * source provider;
  * source provider work identity;
  * normalization version;
  * document title;
  * ordered sections;
  * ordered paragraphs.
* Current normalization version is:

  * `grobid-tei-v1`.
* GROBID TEI XML parser implemented.
* XML parsing uses a hardened parser suitable for externally retrieved XML.
* Both standard GROBID TEI and the older OpenAlex GROBID representation are supported.
* TEI namespaces are handled without depending on one namespace layout.
* Main article title extraction implemented.
* Abstract extraction implemented.
* Body-section extraction implemented.
* Nested section paths are preserved when available.
* Stable global paragraph ordinals are assigned during normalization.
* Section ordinals are required to be unique.
* Paragraph ordinals are required to be unique within a normalized document.
* Original `xml:id` values are preserved when available.
* Inline TEI elements are flattened into readable normalized paragraph text.
* Whitespace is deterministically normalized.
* Empty or unusable documents are rejected.
* Non-GROBID artifacts are rejected by the GROBID parser.
* Section heading roles are represented separately from section content type.
* Current heading roles are:

  * `STANDARD`;
  * `TABLE`;
  * `FIGURE`.
* Table-like and figure-like headings do not cause all contained prose to be classified as exclusively table or figure content.
* Upstream structural ambiguity is preserved rather than silently repaired.

A real normalization run for `W3010059221` produced:

* title: `CORPORATE DEFAULT FORECASTING WITH MACHINE LEARNING`;
* normalization version: `grobid-tei-v1`;
* artifact SHA-256: `ae21bed28e5f9ab69878493e474bb41537621bebe692018944ed1cc2311d1d67`;
* 25 normalized sections;
* 119 normalized paragraphs.

Upstream GROBID imperfections such as merged headings are preserved rather than separated using unsupported heuristics.

### Phase 1 — Stable Evidence Addressing

* `EvidenceAddress` domain representation implemented.
* `EvidenceSpan` domain representation implemented.
* Evidence addressing uses:

  * artifact SHA-256;
  * normalization version;
  * paragraph ordinal;
  * zero-based start character offset;
  * zero-based exclusive end character offset.
* Character spans use Python-style half-open semantics:

  * `[start_char, end_char)`.
* Evidence coordinates and resolved evidence are modelled separately.
* Evidence text is not trusted as part of the address.
* Exact evidence text is resolved deterministically from the normalized document.
* Evidence resolution rejects:

  * incorrect artifact identity;
  * incorrect normalization version;
  * missing paragraph ordinals;
  * invalid character ranges;
  * out-of-bounds character ranges.
* `EvidenceSpan` preserves:

  * exact resolved text;
  * address;
  * source provider;
  * source provider identity;
  * section ordinal;
  * section path.
* Existing evidence can be independently re-resolved and verified against the normalized document.
* Modified or fabricated evidence text fails deterministic verification.

A live evidence-resolution diagnostic was successfully executed against the normalized real article `W3010059221`.

The verified address was:

* artifact SHA-256:
  `ae21bed28e5f9ab69878493e474bb41537621bebe692018944ed1cc2311d1d67`;
* normalization version:
  `grobid-tei-v1`;
* section:
  `22`;
* section path:
  `CONCLUSIONS`;
* paragraph:
  `102`;
* character range:
  `[0, 94)`.

The deterministically resolved evidence was:

`This work compares statistical models usually employed in credit risk modelling with ML models`

The evidence was successfully independently verified against the normalized document.

### Phase 1 — Retrieval-Unit Diagnostics

Paragraph-size distribution was measured against the real normalized `W3010059221` document.

The document contained:

* 119 paragraphs.

Character-length distribution:

* minimum: 22;
* median: 372;
* P75: 765;
* P90: 1046;
* P95: 1337;
* maximum: 2377.

Word-count distribution:

* minimum: 3;
* median: 62;
* P75: 114;
* P90: 161;
* P95: 209;
* maximum: 399.

Character-size buckets:

* 8 paragraphs at or below 100 characters;
* 30 paragraphs between 101 and 250 characters;
* 36 paragraphs between 251 and 500 characters;
* 32 paragraphs between 501 and 1000 characters;
* 11 paragraphs between 1001 and 2000 characters;
* 2 paragraphs above 2000 characters.

The diagnostic also showed that very short or very long paragraphs can represent:

* list fragments;
* table labels;
* table-like flattened text;
* appendix structures;
* ordinary prose.

Therefore paragraph size alone is insufficient to justify automatic splitting, merging, or exclusion.

### Verification

The deterministic test suite currently contains:

**63 passing tests.**

The pipeline has additionally been exercised against real OpenAlex metadata, real OpenAlex full-text infrastructure, a real 234 KB GROBID artifact, a real normalized document, and a real exact evidence span.

---

## In Progress

The current implementation boundary ends at exact, deterministically verifiable evidence spans.

The next capability is:

**paragraph-level retrieval.**

The initial retrieval-unit contract is:

`one NormalizedParagraph = one RetrievalUnit`

A retrieval unit should preserve at minimum:

* artifact SHA-256;
* normalization version;
* source provider identity;
* section ordinal;
* section path;
* section kind;
* section heading role;
* paragraph ordinal;
* paragraph text.

No text is split or merged in retrieval-unit construction.

Retrieval ranking and context expansion remain separate concerns.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* `RetrievalUnit` domain representation;
* deterministic retrieval-corpus construction;
* lexical retrieval baseline;
* retrieval evaluation cases;
* retrieval context expansion;
* semantic embedding retrieval;
* hybrid lexical/semantic retrieval;
* vector persistence;
* normalized document persistence;
* Claude-backed evidence extraction;
* structured evidence-extraction artifacts;
* claim ledger;
* adversarial research criticism;
* research-gap analysis;
* dataset availability analysis;
* baseline identification;
* evaluation-metric analysis;
* experiment-feasibility analysis;
* contribution analysis;
* structured Topic Researchability report;
* human approval gate for topic selection;
* persistent research-artifact graph;
* orchestration framework selection;
* PDF document normalization.

The following later-stage work has also not started:

* final thesis topic selection;
* final thesis research question;
* experiment implementation;
* thesis writing;
* final academic audit.

---

## Active Decisions

### Confirmed

* Claude models accessed through the Anthropic API are the default LLM family for autonomous reasoning agents.
* Model-provider concerns remain isolated behind project-controlled boundaries where practical.
* LLM output is not factual evidence.
* Scholarly discovery, bibliographic verification, relevance assessment, source-text acquisition, normalization, retrieval, and evidence extraction are separate concerns.
* Search-planning output is not research evidence.
* The literature search planner must not formulate the final thesis research question.
* The literature search planner must not invent research gaps, findings, datasets, or contributions.
* Planner-driven scholarly discovery uses OpenAlex semantic retrieval.
* OpenAlex lexical retrieval remains available explicitly.
* DOI metadata verification is provider-independent.
* Crossref coverage is not treated as universal DOI coverage.
* Source identity verification remains deterministic where possible.
* Source identity confirmation does not establish source relevance.
* Source relevance does not establish evidential support for a research claim.
* Titles alone are insufficient evidence for relevance classification.
* Missing evidence remains explicit rather than being converted into artificial certainty.
* Duplicate sources are removed before expensive downstream processing.
* Provider-specific operational constraints belong inside integration boundaries.
* Authentication credentials are not stored in provenance artifacts.
* A scholarly source and a retrievable representation are different domain concepts.
* One scholarly source may have multiple textual representations.
* Landing pages are not automatically treated as full-text documents.
* GROBID XML is preferred over PDF when an appropriate machine-readable representation exists.
* Raw downloaded artifacts are identified using SHA-256.
* Document normalization occurs deterministically before LLM reasoning over full scholarly text.
* Normalization algorithms are explicitly versioned.
* Normalized paragraph order is deterministic.
* Section and paragraph ordinals used for provenance must be unique within the normalized document.
* Upstream structural uncertainty is not silently repaired by invented structure.
* Markdown may later be used as an LLM-facing rendering but is not canonical provenance.
* Full libraries of papers are not supplied directly to an LLM context.
* Future reasoning operates over selected evidence derived from normalized documents.
* Evidence coordinates and evidence text are separate concepts.
* Evidence text is deterministically resolved from coordinates.
* Evidence addresses include both raw artifact identity and normalization version.
* Evidence offsets are zero-based half-open character ranges.
* Inability to retrieve full text is a valid explicit outcome.
* Full-text resolution does not become an unbounded provider-search loop.
* Paragraphs are the initial retrieval units.
* Paragraphs are not automatically merged or split before empirical retrieval evaluation.
* Retrieval ranking and contextual expansion are separate concerns.
* Embeddings and vector storage are not introduced before a simpler retrieval baseline is measured.
* Agent execution must be bounded.
* Important project state is externalised into repository artifacts.
* Human approval is required for consequential research decisions.
* Technology is selected in response to executable requirements rather than anticipated future complexity.
* Every pull request targeting `main` must update `CURRENT_STATE.md`.
* The repository Current State Gate should prevent merge when that invariant is violated.

### Not Yet Decided

* final thesis topic;
* final thesis research question;
* exact Claude model allocation by agent role;
* orchestration framework;
* persistence technology;
* vector retrieval technology;
* embedding model;
* lexical retrieval implementation;
* retrieval scoring strategy;
* retrieval context-expansion policy;
* retrieval evaluation metric set;
* execution sandbox;
* experiment tracking system;
* observability stack;
* deployment architecture;
* final agent topology;
* final provenance persistence schema;
* final evaluation framework;
* PDF parsing technology;
* whether hybrid retrieval is required;
* whether a vector database is required;
* whether a dedicated workflow engine is required;
* whether future normalization versions should represent tables and figures as independent document nodes.

---

## Current Risks

### RISK-001 — Premature architecture

The project may adopt orchestration, persistence, retrieval, or agent frameworks before concrete workflow requirements justify them.

**Mitigation:** continue implementing minimal executable slices and measure behaviour before selecting infrastructure.

### RISK-002 — Model-generated false certainty

Claude or another reasoning model may classify or interpret research artifacts more confidently than the available evidence supports.

**Mitigation:** use structured outputs, explicit uncertainty states, deterministic gates, external evidence, exact evidence addresses, and evaluation.

### RISK-003 — Relevance misclassification

A scholarly search provider may return legitimate but topically irrelevant publications, and an LLM relevance classifier may make incorrect relevance judgments.

**Mitigation:** keep discovery separate from relevance assessment, maintain explicit evaluation cases, and preserve uncertainty.

### RISK-004 — Incomplete scholarly metadata

Different scholarly providers may expose different author names, publication dates, venue representations, DOI coverage, or missing abstracts.

**Mitigation:** preserve provider-specific discrepancies and support multiple metadata registries.

### RISK-005 — Unbounded agent cost

Future autonomous research or review loops may consume excessive model calls and tokens without meaningful progress.

**Mitigation:** use explicit search fan-out limits and introduce additional execution budgets before broader autonomous loops.

### RISK-006 — Documentation drift

Canonical documentation may fall behind runtime state.

**Mitigation:** every pull request targeting `main` must update `CURRENT_STATE.md`, enforced by CI. Executable code and tests remain authoritative for runtime behaviour.

### RISK-007 — Incomplete full-text availability

A material subset of relevant scholarly sources may not expose usable open full text through the supported resolver.

**Mitigation:** preserve explicit text-unavailable states and avoid unbounded provider searching.

### RISK-008 — Retrieval quality

A retrieval algorithm may rank broad methodological text, table fragments, or short structural fragments above evidence directly useful for the research task.

**Mitigation:** establish a deterministic lexical baseline, build explicit retrieval evaluation cases, preserve structural metadata, and measure failure modes before introducing semantic or hybrid retrieval.

### RISK-009 — Document parsing fidelity

Machine-readable scholarly representations may lose, alter, merge, or restructure information from the original publication.

**Mitigation:** preserve immutable raw artifact identity, version normalization, preserve upstream ambiguity, avoid unsupported reconstruction, and validate parsing on real documents.

### RISK-010 — Provider-authenticated artifact access

Some OpenAlex-hosted cached full-text artifacts require authenticated access.

**Mitigation:** keep authentication ephemeral and provider-specific; never embed credentials into provenance artifacts.

### RISK-011 — Evidence-address instability

Offsets or paragraph identities may change if normalization logic changes.

**Mitigation:** evidence addresses include artifact identity and normalization version; resolution fails when either does not match.

### RISK-012 — Retrieval-unit quality

Very short paragraphs may lack sufficient standalone context, while some long paragraphs contain flattened table-like structures.

**Mitigation:** preserve paragraph boundaries in retrieval-unit v1, retain section metadata, evaluate retrieval empirically, and introduce context expansion or filtering only in response to measured failures.

---

## Known Unknowns

The authoritative list of major unresolved project questions is maintained in `PROJECT.md`.

Current high-priority unknowns are:

1. University thesis requirements.
2. University policy for AI-assisted academic work.
3. Final FinTech thesis topic.
4. Reliable criteria for determining topic researchability.
5. Data availability for candidate research topics.
6. How much source text is required before a source can support a research claim rather than merely pass relevance assessment.
7. Whether current open-access text resolution provides sufficient coverage across realistic thesis literature.
8. How lexical paragraph retrieval performs on realistic research questions.
9. Whether headings should participate directly in retrieval scoring or only as metadata.
10. When adjacent paragraphs should be added as context after retrieval.
11. Whether semantic embeddings materially improve evidence retrieval over the lexical baseline.
12. Whether hybrid retrieval is necessary.
13. Whether a dedicated vector database is justified.
14. How evidence derived from tables, figures, equations, or other non-prose structures should eventually be represented.
15. How PDF-only documents should be normalized.
16. Whether orchestration requirements will justify a dedicated workflow framework.
17. Which persistence representation should eventually store source → artifact → document → retrieval → evidence → claim relationships.

---

## Next Actions

1. Define a minimal immutable `RetrievalUnit` model.
2. Implement deterministic conversion from every normalized paragraph to one retrieval unit.
3. Preserve source, artifact, normalization, section, heading-role, and paragraph metadata on each unit.
4. Do not merge or split paragraph text in retrieval-unit v1.
5. Build a deterministic retrieval corpus from a normalized document.
6. Implement the simplest measurable lexical retrieval baseline.
7. Define explicit retrieval evaluation queries and expected relevant paragraph sets.
8. Evaluate lexical ranking against the real `W3010059221` document.
9. Inspect errors involving short fragments, tables, appendices, and neighbouring context.
10. Decide whether context expansion is necessary.
11. Only then evaluate semantic embeddings.
12. Introduce vector persistence only if empirical retrieval requirements justify it.
13. Introduce Claude-backed evidence extraction only after retrieval returns sufficiently reliable candidate passages.

---

## Current Milestone Exit Criteria

The initial Topic Researchability milestone is complete when:

* a candidate topic can drive bounded scholarly literature planning;
* planned searches can drive scholarly literature discovery;
* duplicate discoveries can be consolidated without losing query provenance;
* discovered sources can be bibliographically verified;
* source relevance can be assessed with explicit uncertainty;
* insufficient evidence remains explicit;
* usable scholarly full text can be resolved where available;
* retrieved artifacts have immutable identity and preserved provenance;
* scholarly artifacts can be deterministically normalized;
* exact evidence spans can be addressed and independently verified;
* relevant passages can be retrieved without supplying an entire literature corpus to an LLM;
* retrieval behaviour is evaluated against explicit cases;
* relevant evidence can be extracted with provenance;
* plausible research gaps can be evaluated adversarially;
* data availability and experimental feasibility can be assessed;
* researchability dimensions can be assembled into a structured report;
* unresolved questions remain explicit;
* a human can approve, reject, or request further research on a candidate topic;
* the complete decision path is auditable from repository artifacts.
