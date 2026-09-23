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
* exact evidence addressing and verification;
* paragraph-level retrieval;
* deterministic BM25 lexical ranking.

The project is now moving from an operational retrieval baseline toward measurable retrieval evaluation.

---

## Current Objective

Establish a repeatable retrieval evaluation framework before introducing semantic embeddings or vector infrastructure.

The current focus is:

**retrieval evaluation over normalized scholarly evidence.**

Paragraph-level BM25 retrieval is operational and has performed well on an initial real scholarly document.

However, the initial real diagnostic queries intentionally contained substantial lexical overlap with the source text.

The next capability must evaluate retrieval using explicit relevance labels and harder paraphrased queries so that future semantic or hybrid retrieval can be compared against a meaningful baseline rather than against intuition.

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

For the candidate topic:

`machine learning credit risk`

a five-query semantic discovery run with five results per query produced:

* 25 unique scholarly sources;
* 14 `RELEVANT`;
* 0 `NOT_RELEVANT`;
* 0 `UNCERTAIN`;
* 9 `INSUFFICIENT_EVIDENCE`;
* 2 sources that could not proceed to relevance assessment because bibliographic verification could not be completed.

This demonstrated that textual evidence availability was a more material bottleneck than initial scholarly retrieval precision.

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

Incomplete full-text coverage is treated as an explicit supported state rather than as a trigger for unbounded provider searching.

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
* Current normalization version is `grobid-tei-v1`.
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
* Table-like and figure-like headings do not imply that every contained paragraph exclusively represents table or figure content.
* Upstream structural ambiguity is preserved rather than silently repaired.

A real normalization run for `W3010059221` produced:

* title: `CORPORATE DEFAULT FORECASTING WITH MACHINE LEARNING`;
* normalization version: `grobid-tei-v1`;
* artifact SHA-256: `ae21bed28e5f9ab69878493e474bb41537621bebe692018944ed1cc2311d1d67`;
* 25 normalized sections;
* 119 normalized paragraphs.

### Phase 1 — Stable Evidence Addressing

* `EvidenceAddress` implemented.
* `EvidenceSpan` implemented.
* Evidence addressing uses:

  * artifact SHA-256;
  * normalization version;
  * paragraph ordinal;
  * zero-based start character offset;
  * zero-based exclusive end character offset.
* Character spans use half-open `[start_char, end_char)` semantics.
* Evidence coordinates and resolved evidence are modelled separately.
* Evidence text is not trusted as part of the address.
* Exact evidence text is resolved deterministically from the normalized document.
* Evidence resolution rejects:

  * incorrect artifact identity;
  * incorrect normalization version;
  * missing paragraph ordinals;
  * invalid character ranges;
  * out-of-bounds ranges.
* Resolved evidence preserves source and section provenance.
* Existing evidence can be independently re-resolved and verified.
* Modified or fabricated evidence text fails deterministic verification.

A live evidence diagnostic successfully resolved and verified:

* section: `CONCLUSIONS`;
* paragraph: `102`;
* character range: `[0, 94)`.

Resolved text:

`This work compares statistical models usually employed in credit risk modelling with ML models`

### Phase 1 — Retrieval-Unit Diagnostics

Paragraph-size distribution was measured against real normalized work `W3010059221`.

The document contained 119 paragraphs.

Character distribution:

* minimum: 22;
* median: 372;
* P75: 765;
* P90: 1046;
* P95: 1337;
* maximum: 2377.

Word distribution:

* minimum: 3;
* median: 62;
* P75: 114;
* P90: 161;
* P95: 209;
* maximum: 399.

The distribution supports the initial decision:

`one NormalizedParagraph = one RetrievalUnit`

without automatic paragraph splitting or merging.

The diagnostic also demonstrated that size alone cannot safely classify retrieval quality because very short and very long paragraphs can contain:

* genuine prose;
* list fragments;
* table labels;
* flattened tables;
* appendix structures.

### Phase 1 — Paragraph Retrieval Baseline

* Immutable `RetrievalUnit` representation implemented.
* Retrieval units preserve:

  * artifact SHA-256;
  * normalization version;
  * source provider;
  * source provider identity;
  * section ordinal;
  * section path;
  * section kind;
  * heading role;
  * paragraph ordinal;
  * exact normalized paragraph text.
* Deterministic retrieval-corpus construction implemented.
* Every normalized paragraph becomes exactly one retrieval unit.
* Retrieval-unit construction does not split, merge, rewrite, summarize, or otherwise transform paragraph text.
* Duplicate retrieval-unit identities are rejected.
* Deterministic BM25 lexical retriever implemented without introducing an external search dependency.
* BM25 indexing currently uses:

  * section path;
  * paragraph text.
* Section headings therefore contribute to retrieval ranking without becoming evidence text.
* Search is case-insensitive.
* Zero-score units are not returned.
* Ranking ties are resolved deterministically by corpus order.
* `top_k` is explicitly bounded by the caller.

A live BM25 diagnostic was executed over all 119 paragraphs of `W3010059221`.

Five research-oriented queries were tested:

* machine-learning model description;
* credit-allocation effects;
* credit behavioral indicators;
* backtesting;
* variable importance.

For all five queries, the highest-ranked paragraph was substantively relevant to the requested concept.

Examples include:

* ML models → paragraph 28, `MACHINE LEARNING MODELS`;
* credit allocation → paragraph 105, `CONCLUSIONS`;
* credit behavioral indicators → paragraph 48, `FINANCIAL AND CREDIT BEHAVIORAL INDICATORS`;
* backtesting → paragraph 78, `BACKTESTING`;
* variable importance → paragraph 97, `VARIABLE IMPORTANCE AND MODEL ROBUSTNESS`.

The diagnostic also exposed retrieval noise below the highest-ranked results.

Observed noise includes:

* flattened tabular content;
* appendix tables;
* short table labels;
* figure-associated sections.

Examples include paragraphs 99, 117, and 118 appearing highly because they contain many exact query terms.

No filtering has been introduced in response to these cases because sections with table-like headings can also contain genuine prose.

### Verification

The deterministic test suite currently contains:

**73 passing tests.**

The pipeline has additionally been exercised against:

* real OpenAlex metadata;
* real OpenAlex full-text infrastructure;
* a real 234 KB GROBID artifact;
* a real normalized scholarly document;
* a real exact evidence span;
* a real 119-unit BM25 retrieval corpus.

---

## In Progress

The current implementation boundary ends at a working deterministic lexical retrieval baseline.

The next capability is:

**retrieval evaluation.**

The retrieval system must be evaluated against explicitly labelled cases before semantic embeddings, hybrid retrieval, reranking, context expansion, or vector storage are introduced.

Evaluation should distinguish at least:

* exact or near-exact lexical queries;
* paraphrased conceptual queries with reduced lexical overlap.

Initial evaluation metrics should measure:

* whether at least one relevant passage appears in the top K;
* how early the first relevant passage appears;
* how much of the labelled relevant set is recovered.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* structured retrieval-evaluation cases;
* deterministic retrieval evaluation harness;
* Recall@K measurement;
* reciprocal-rank measurement;
* Hit@K measurement;
* semantic/paraphrase retrieval stress tests;
* contextual-neighbour expansion;
* semantic embedding retrieval;
* hybrid lexical/semantic retrieval;
* reranking;
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
* Missing evidence remains explicit.
* Duplicate sources are removed before expensive downstream processing.
* Provider-specific operational constraints belong inside integration boundaries.
* Authentication credentials are not stored in provenance artifacts.
* A scholarly source and a retrievable representation are different domain concepts.
* One scholarly source may have multiple textual representations.
* Landing pages are not automatically treated as full-text documents.
* GROBID XML is preferred over PDF when appropriate machine-readable representation exists.
* Raw downloaded artifacts are identified using SHA-256.
* Document normalization occurs deterministically before LLM reasoning over full scholarly text.
* Normalization algorithms are explicitly versioned.
* Normalized paragraph order is deterministic.
* Section and paragraph ordinals used for provenance must be unique within a normalized document.
* Upstream structural uncertainty is not silently repaired by invented structure.
* Markdown may later be used as an LLM-facing rendering but is not canonical provenance.
* Full libraries of papers are not supplied directly to an LLM context.
* Evidence coordinates and evidence text are separate concepts.
* Evidence text is deterministically resolved from coordinates.
* Evidence addresses include raw artifact identity and normalization version.
* Evidence offsets are zero-based half-open character ranges.
* Inability to retrieve full text is a valid explicit outcome.
* Full-text resolution does not become an unbounded provider-search loop.
* One normalized paragraph is one retrieval unit in retrieval v1.
* Retrieval-unit text is not automatically split or merged.
* Section paths participate in lexical indexing but are not treated as evidence text.
* BM25 is the initial deterministic lexical retrieval baseline.
* Retrieval ranking and contextual expansion remain separate concerns.
* Retrieval quality must be evaluated before semantic retrieval is introduced.
* Embeddings and vector storage are not introduced merely because they are conventional in RAG systems.
* Table- or figure-associated paragraphs are not automatically excluded from retrieval.
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
* embedding model;
* semantic retrieval technology;
* vector retrieval technology;
* retrieval context-expansion policy;
* hybrid retrieval strategy;
* reranking strategy;
* retrieval score-combination strategy;
* final retrieval evaluation metric set;
* execution sandbox;
* experiment tracking system;
* observability stack;
* deployment architecture;
* final agent topology;
* final provenance persistence schema;
* final evaluation framework;
* PDF parsing technology;
* whether semantic retrieval materially improves the lexical baseline;
* whether hybrid retrieval is necessary;
* whether a vector database is required;
* whether a dedicated workflow engine is required;
* whether tables and figures eventually require independent first-class normalized nodes.

---

## Current Risks

### RISK-001 — Premature architecture

The project may adopt infrastructure before executable requirements justify it.

**Mitigation:** continue implementing minimal measurable slices before selecting infrastructure.

### RISK-002 — Model-generated false certainty

LLMs may interpret evidence more confidently than the underlying material supports.

**Mitigation:** structured outputs, explicit uncertainty, deterministic evidence addressing, external evidence, and independent verification.

### RISK-003 — Relevance misclassification

Scholarly retrieval and LLM relevance classification may both produce incorrect relevance judgments.

**Mitigation:** separate discovery from relevance assessment and preserve uncertainty.

### RISK-004 — Incomplete scholarly metadata

Different scholarly providers expose incomplete or inconsistent metadata.

**Mitigation:** preserve discrepancies and use multiple metadata registries behind provider-independent boundaries.

### RISK-005 — Unbounded agent cost

Future autonomous loops may consume excessive calls or tokens.

**Mitigation:** bounded search fan-out and explicit execution budgets.

### RISK-006 — Documentation drift

Canonical documentation may fall behind runtime state.

**Mitigation:** every pull request targeting `main` updates `CURRENT_STATE.md`, enforced by CI.

### RISK-007 — Incomplete full-text availability

Some relevant scholarly sources do not expose usable open full text.

**Mitigation:** preserve explicit text-unavailable states and avoid unbounded provider searching.

### RISK-008 — Retrieval quality

Lexical retrieval may fail when research questions and evidence use different terminology.

**Mitigation:** establish an explicit BM25 baseline, evaluate paraphrased queries, and introduce semantic retrieval only when measured results justify it.

### RISK-009 — Document parsing fidelity

Machine-readable scholarly representations may merge or restructure original publication content.

**Mitigation:** preserve raw artifact identity, version normalization, and avoid unsupported structural reconstruction.

### RISK-010 — Provider-authenticated artifact access

Some full-text artifacts require authenticated access.

**Mitigation:** credentials remain ephemeral and outside provenance artifacts.

### RISK-011 — Evidence-address instability

Normalization changes may invalidate old paragraph and character addresses.

**Mitigation:** every address includes artifact identity and normalization version.

### RISK-012 — Retrieval-unit quality

Short structural fragments and flattened tables can receive strong lexical scores despite being poor standalone evidence candidates.

**Mitigation:** preserve them initially, measure their effect through retrieval evaluation, and introduce filtering or reranking only in response to demonstrated failure modes.

### RISK-013 — Evaluation-set bias

A retrieval benchmark built from queries copied directly from paper terminology can overestimate lexical retrieval quality.

**Mitigation:** include independently phrased conceptual queries with reduced lexical overlap and keep relevance labels separate from query generation.

---

## Known Unknowns

The authoritative list of major unresolved project questions is maintained in `PROJECT.md`.

Current high-priority unknowns are:

1. University thesis requirements.
2. University policy for AI-assisted academic work.
3. Final FinTech thesis topic.
4. Reliable criteria for determining topic researchability.
5. Data availability for candidate research topics.
6. How much source text is required before a source can support a research claim.
7. Whether current open-access text resolution provides sufficient coverage.
8. How BM25 performs on conceptual queries with weak lexical overlap.
9. Whether headings should receive different retrieval weight from paragraph text.
10. Whether neighbouring paragraphs should be added after retrieval.
11. Whether semantic embeddings materially improve retrieval.
12. Whether hybrid lexical/semantic retrieval is required.
13. Whether reranking is required.
14. Whether vector persistence is justified.
15. How tables, figures, equations, and other non-prose evidence should eventually be represented.
16. How PDF-only documents should be normalized.
17. Whether orchestration requirements justify a dedicated workflow framework.
18. Which persistence representation should store source → artifact → document → retrieval → evidence → claim relationships.

---

## Next Actions

1. Define a structured retrieval-evaluation case.
2. Allow one query to reference multiple relevant paragraph ordinals.
3. Define a minimal retriever interface suitable for evaluating BM25 and future retrievers.
4. Implement deterministic Hit@K.
5. Implement Recall@K.
6. Implement reciprocal rank and mean reciprocal rank.
7. Create a small initial labelled evaluation set for `W3010059221`.
8. Include both direct lexical queries and independently phrased conceptual queries.
9. Run the BM25 baseline against the evaluation set.
10. Inspect failures rather than immediately modifying ranking.
11. Decide whether lexical weighting, context expansion, semantic retrieval, or another capability addresses the measured failures.
12. Only then introduce embeddings if justified.
13. Introduce Claude-backed evidence extraction only after retrieval quality is sufficiently measurable and reliable.

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
* retrieved artifacts have immutable identity and provenance;
* scholarly artifacts can be deterministically normalized;
* exact evidence spans can be addressed and independently verified;
* relevant passages can be retrieved without supplying an entire corpus to an LLM;
* retrieval behaviour is evaluated against explicit labelled cases;
* relevant evidence can be extracted with provenance;
* plausible research gaps can be evaluated adversarially;
* data availability and experimental feasibility can be assessed;
* researchability dimensions can be assembled into a structured report;
* unresolved questions remain explicit;
* a human can approve, reject, or request further research on a candidate topic;
* the complete decision path is auditable from repository artifacts.
