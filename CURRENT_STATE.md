# Current Project State

Last updated: 2026-09-24

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
* multi-document paragraph retrieval;
* deterministic BM25 lexical ranking;
* embedding-based semantic retrieval;
* deterministic reciprocal-rank fusion experimentation;
* human-reviewed retrieval benchmarking;
* lexical-versus-semantic-versus-hybrid retrieval comparison;
* source-pinned university thesis requirements;
* deterministic university-fit evaluation;
* structured topic-researchability decision state.

The initial retrieval architecture experiments are complete.

BM25 and semantic retrieval exhibit complementary failure modes.

Voyage semantic retrieval is currently the strongest standalone measured baseline.

A deterministic Reciprocal Rank Fusion hybrid was implemented and evaluated, but it did not improve the current semantic baseline sufficiently to justify selection.

University thesis requirements from the supplied ELTE Faculty of Informatics dissertation guide have now been represented explicitly rather than remaining implicit human context.

Topic researchability can now represent university fit together with literature, dataset, baseline, metric, experiment-feasibility, and contribution dimensions while preserving unresolved dimensions as `UNKNOWN`.

The next major technical objective is to challenge the current retrieval conclusions on held-out scholarly evidence before beginning evidence-driven researchability assessment.

---

## Current Objective

Establish a held-out retrieval evaluation that can test whether the observed BM25, semantic, and hybrid behaviours generalize beyond:

`credit-risk-two-paper-v2`

The current twelve-case benchmark remains a regression and architecture-comparison benchmark.

It must not become a tuning target for additional fusion parameters, weights, rerankers, source-diversity rules, or benchmark-specific heuristics.

Before retrieval architecture is considered sufficiently stable for evidence extraction, the system should be evaluated on additional documents and research questions that were not used to make the current retrieval decisions.

The next evaluation should preserve:

* explicit evidence targets;
* immutable source-artifact identities;
* paragraph-level retrieval units;
* fixed evaluation inputs before system comparison;
* deterministic metrics;
* no case-specific retrieval heuristics;
* no unnecessary vector database;
* no LLM reranker unless a measured requirement later justifies one.

In parallel, the new university-fit and topic-researchability models establish the decision contract that later evidence-analysis capabilities must populate.

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
* Search planning is separated from final thesis research-question formulation.
* Search plans are limited to at most five complementary scholarly search tasks.
* Search-planning output is operational metadata and is not treated as research evidence.
* Topic-level literature assessment workflow implemented.
* Results from multiple searches are aggregated before downstream processing.
* Duplicate scholarly sources are removed before bibliographic verification and relevance assessment.
* Search-query provenance is preserved.
* OpenAlex lexical and semantic search modes implemented explicitly.
* Live diagnostics demonstrated substantially better topical precision from OpenAlex semantic retrieval than lexical retrieval for the current candidate topic.
* Planner-driven literature discovery currently uses OpenAlex semantic search.
* Crossref abstracts can act as fallback textual evidence when OpenAlex does not expose an abstract.

### Phase 1 — Real Literature Workflow Validation

For the candidate topic:

`machine learning credit risk`

a five-query semantic discovery run with five results per query produced:

* 25 unique scholarly sources;
* 14 `RELEVANT`;
* 0 `NOT_RELEVANT`;
* 0 `UNCERTAIN`;
* 9 `INSUFFICIENT_EVIDENCE`;
* 2 sources unable to proceed because bibliographic verification could not be completed.

This demonstrated that textual evidence availability was a material bottleneck after discovery.

### Phase 1 — Source-Text Resolution

* `SourceTextLocation` introduced separately from `SourceRecord`.
* Bibliographic identity and textual representation are distinct domain concepts.
* OpenAlex full-text location lookup implemented.
* OpenAlex `best_oa_location`, complete `locations`, and cached `content_urls` are supported.
* Supported location representations include:

  * OpenAlex GROBID XML;
  * OpenAlex cached PDF;
  * original open-access PDF;
  * scholarly landing page.
* Locations are deduplicated.
* Landing pages are not treated as downloadable full text.
* Preferred text-location order is:

  1. OpenAlex GROBID XML;
  2. OpenAlex cached PDF;
  3. original open-access PDF.
* Missing full text is an explicit supported outcome.
* Full-text resolution does not trigger unbounded provider searching.

### Phase 1 — Artifact Acquisition

* Deterministic artifact fetching implemented.
* Supported artifact formats currently include GROBID XML and PDF.
* Empty artifacts are rejected.
* Invalid PDF responses are rejected.
* Maximum artifact size is bounded.
* Downloaded artifact bytes receive deterministic SHA-256 identity.
* Authentication credentials are not stored in provenance artifacts.

A real OpenAlex GROBID artifact for:

`Corporate default forecasting with machine learning`

was downloaded with:

* OpenAlex work: `W3010059221`;
* size: `234692` bytes;
* SHA-256:
  `ae21bed28e5f9ab69878493e474bb41537621bebe692018944ed1cc2311d1d67`.

### Phase 1 — Scholarly Document Normalization

* `NormalizedDocument` implemented.
* `NormalizedSection` implemented.
* `NormalizedParagraph` implemented.
* Current normalization version is:
  `grobid-tei-v1`.
* GROBID TEI parser implemented using hardened XML parsing.
* Standard GROBID TEI and legacy OpenAlex GROBID forms are supported.
* Namespace differences are handled.
* Title, abstract, sections, nested paths, paragraphs, and available `xml:id` values are preserved.
* Paragraph whitespace is normalized deterministically.
* Section and paragraph ordinals are deterministic and unique within a document.
* Section heading roles are represented separately from section content type.
* Current heading roles are:

  * `STANDARD`;
  * `TABLE`;
  * `FIGURE`.
* Table- or figure-like headings do not cause all contained paragraphs to be treated as non-prose.
* Upstream GROBID structural ambiguities are preserved rather than heuristically repaired.

Real normalization of `W3010059221` produced:

* 25 sections;
* 119 paragraphs.

A second real article:

`Enhancing Credit Scoring with Alternative Data`

OpenAlex work:

`W3044323082`

was also normalized successfully, producing:

* 20 sections;
* 93 paragraphs;
* artifact SHA-256:
  `640d703f9028b31a6ed1336b8deb38261a93cad81957616972ed8041ba3cf034`.

### Phase 1 — Stable Evidence Addressing

* `EvidenceAddress` implemented.
* `EvidenceSpan` implemented.
* Evidence addresses contain:

  * artifact SHA-256;
  * normalization version;
  * paragraph ordinal;
  * zero-based start character offset;
  * zero-based exclusive end character offset.
* Character spans use `[start_char, end_char)` semantics.
* Evidence coordinates and evidence text are separate concepts.
* Evidence text is deterministically resolved from the normalized document.
* Wrong artifact identities, normalization versions, paragraph ordinals, and character ranges are rejected.
* Evidence can be independently re-resolved and verified.
* Fabricated or modified evidence text fails deterministic verification.

A live evidence diagnostic successfully resolved and verified an exact passage from paragraph 102 of `W3010059221`.

### Phase 1 — Retrieval-Unit Diagnostics

Paragraph-size distribution was measured on real scholarly text before choosing a chunking strategy.

For `W3010059221`:

* 119 paragraphs;
* median: 372 characters / 62 words;
* P95: 1337 characters / 209 words;
* maximum: 2377 characters / 399 words.

This supported the initial retrieval decision:

`one NormalizedParagraph = one RetrievalUnit`

No automatic paragraph splitting or merging is currently performed.

### Phase 1 — Multi-Document Retrieval Corpus

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
  * exact normalized text.
* Canonical `RetrievalUnitId` implemented using:

  * artifact SHA-256;
  * normalization version;
  * paragraph ordinal.
* Retrieval identity remains unambiguous across multiple scholarly documents.
* Deterministic single-document retrieval-unit construction implemented.
* Deterministic multi-document retrieval-corpus construction implemented.
* Duplicate retrieval-unit identities are rejected.

The current real benchmark corpus contains:

* 2 scholarly documents;
* 212 retrieval units.

### Phase 1 — BM25 Retrieval Baseline

* Dependency-free deterministic BM25 lexical retrieval implemented.
* BM25 indexing currently uses:

  * section path;
  * paragraph text.
* Original paragraph text remains unchanged.
* Section headings therefore contribute to discovery but do not become evidence.
* Search is case-insensitive.
* Zero-score units are excluded.
* Ranking ties are deterministic.
* Caller specifies bounded `top_k`.

Initial real diagnostics demonstrated good lexical retrieval while also exposing:

* table and appendix noise;
* heading-driven matches;
* weak paraphrase handling;
* incomplete multi-facet evidence recovery.

No heuristic filtering was introduced in response to those observations.

### Phase 1 — Semantic Retrieval Baseline

* Provider-independent `TextEmbedder` protocol implemented.
* In-memory `SemanticRetriever` implemented.
* Semantic retrieval operates over the same canonical `RetrievalUnit` corpus as BM25.
* Document embedding text currently contains:

  * section path;
  * exact normalized paragraph text.
* Semantic ranking uses cosine similarity.
* No vector database is required for the current 212-unit corpus.
* Retrieval-domain scoring was generalized to permit any finite score rather than assuming every retriever emits only positive values.
* Query and document embeddings remain separate operations.

### Phase 1 — Voyage Embedding Integration

* Voyage AI embedding integration implemented behind the project-controlled embedding boundary.
* Current semantic baseline model:
  `voyage-4`.
* Voyage is an implementation of the embedding boundary rather than a dependency of the retrieval domain.
* Queries use Voyage `query` input type.
* Retrieval units use Voyage `document` input type.
* Silent provider-side text truncation is disabled.
* Provider responses are validated for:

  * expected embedding count;
  * unique embedding indices;
  * complete embedding indices;
  * consistent dimensions;
  * finite numeric values.
* Embeddings are restored to caller order using provider response indices.
* Document embedding requests are bounded into batches.
* Retryable provider failures use bounded retry.
* HTTP `429` and transient server failures are handled as retryable outcomes.
* `Retry-After` is respected when available.
* Exponential backoff is bounded.
* Request pacing is configurable.
* Current default configuration is compatible with the reduced no-payment-method Voyage limits used during development:

  * batch size: `24`;
  * minimum request interval: `21` seconds.
* No API credentials are persisted in project artifacts or provenance.
* Live Voyage embedding generation has been successfully executed against the real retrieval corpus.

### Phase 1 — Retrieval Evaluation Framework

* Generic `Retriever` protocol implemented.
* Retrieval evaluation is independent of BM25 and can be reused for semantic and hybrid retrievers.
* Query style and evaluation scope are represented as separate dimensions.

Current query styles:

* `LEXICAL`;
* `PARAPHRASE`.

Current scopes:

* `SINGLE_DOCUMENT`;
* `SOURCE_SELECTION`;
* `CROSS_DOCUMENT`.

The initial exhaustive relevance-list approach was rejected after audit because the benchmark did not contain complete relevance judgements for all 212 passages.

The evaluation model uses evidence targets.

Each `RetrievalTarget` describes:

* one evidence requirement;
* one or more acceptable passages capable of satisfying that requirement.

This avoids treating unlabelled but valid passages as automatically irrelevant.

Current metrics are:

* `Hit@K` — whether at least one evidence target was satisfied;
* `Complete@K` — whether every required target was satisfied;
* `Target Coverage@K` — fraction of required evidence targets satisfied;
* reciprocal rank — rank of the first acceptable evidence anchor;
* MRR — mean reciprocal rank across cases.

### Phase 1 — Human-Reviewed Retrieval Benchmark

A persistent benchmark exists at:

`evals/retrieval/baseline_v2.json`

Benchmark name:

`credit-risk-two-paper-v2`

The benchmark is pinned to the exact SHA-256 identities of both real scholarly artifacts.

It contains:

* 12 human-reviewed research queries;
* 16 evidence targets;
* lexical and paraphrased queries;
* single-document questions;
* source-selection questions;
* cross-document questions.

Acceptable evidence anchors were reviewed against the canonical 212-unit corpus.

Retriever output is not treated as exhaustive ground truth.

The benchmark evaluates whether retrieval supplies evidence sufficient to satisfy explicit research requirements rather than pretending that every relevant paragraph has been exhaustively labelled.

### Phase 1 — Measured BM25 Benchmark

BM25 was evaluated at `K = 5`.

Overall:

* cases: 12;
* `Hit@5`: `0.9167`;
* `Complete@5`: `0.7500`;
* `Target Coverage@5`: `0.8333`;
* MRR: `0.6319`.

Lexical queries:

* cases: 5;
* `Hit@5`: `1.0000`;
* `Complete@5`: `1.0000`;
* `Target Coverage@5`: `1.0000`;
* MRR: `0.8667`.

Paraphrased queries:

* cases: 7;
* `Hit@5`: `0.8571`;
* `Complete@5`: `0.5714`;
* `Target Coverage@5`: `0.7143`;
* MRR: `0.4643`.

Single-document queries:

* cases: 8;
* `Hit@5`: `0.8750`;
* `Complete@5`: `0.7500`;
* `Target Coverage@5`: `0.8125`;
* MRR: `0.5312`.

Source-selection queries:

* cases: 2;
* `Hit@5`: `1.0000`;
* `Complete@5`: `1.0000`;
* `Target Coverage@5`: `1.0000`;
* MRR: `1.0000`.

Cross-document queries:

* cases: 2;
* `Hit@5`: `1.0000`;
* `Complete@5`: `0.5000`;
* `Target Coverage@5`: `0.7500`;
* MRR: `0.6667`.

### Phase 1 — Measured Semantic Benchmark

Voyage `voyage-4` semantic retrieval was evaluated over exactly the same:

* two scholarly artifacts;
* 212 retrieval units;
* 12 benchmark cases;
* 16 evidence targets;
* `K = 5`.

Overall semantic result:

* `Hit@5`: `0.9167`;
* `Complete@5`: `0.8333`;
* `Target Coverage@5`: `0.8750`;
* MRR: `0.8194`.

Relative to BM25:

* `Hit@5`: unchanged;
* `Complete@5`: `+0.0833`;
* `Target Coverage@5`: `+0.0417`;
* MRR: `+0.1875`.

Lexical queries:

* `Hit@5`: `1.0000`;
* `Complete@5`: `1.0000`;
* `Target Coverage@5`: `1.0000`;
* MRR: `0.8667`.

Paraphrased queries:

* `Hit@5`: `0.8571`;
* `Complete@5`: `0.7143`;
* `Target Coverage@5`: `0.7857`;
* MRR: `0.7857`.

Single-document queries:

* `Hit@5`: `0.8750`;
* `Complete@5`: `0.8750`;
* `Target Coverage@5`: `0.8750`;
* MRR: `0.7292`.

Source-selection queries:

* `Hit@5`: `1.0000`;
* `Complete@5`: `1.0000`;
* `Target Coverage@5`: `1.0000`;
* MRR: `1.0000`.

Cross-document queries:

* `Hit@5`: `1.0000`;
* `Complete@5`: `0.5000`;
* `Target Coverage@5`: `0.7500`;
* MRR: `1.0000`.

### Phase 1 — Lexical and Semantic Complementarity

Measured comparison established complementary failure modes:

* semantic retrieval recovered `combined_nontraditional_predictors`, which BM25 missed;
* semantic retrieval recovered both sample-size targets in `sample_size_sensitivity_cross_paper`, while BM25 recovered one;
* BM25 retained evidence for `ml_advantage_conditions` that semantic retrieval missed;
* BM25 retained both cross-paper information-richness targets where semantic retrieval concentrated on one source.

Semantic retrieval therefore materially improved ranking quality but did not dominate lexical retrieval on every evidence requirement.

### Phase 1 — Hybrid Retrieval Experiment

A minimal deterministic hybrid retriever was implemented using Reciprocal Rank Fusion.

The implementation:

* accepts lexical and semantic child retrievers;
* requests bounded candidate lists;
* combines ranks rather than incomparable raw scores;
* deduplicates candidates using canonical `RetrievalUnitId`;
* rejects duplicate or conflicting unit identities;
* produces deterministic ordering.

The only evaluated configuration was:

* BM25 lexical retrieval;
* Voyage `voyage-4` semantic retrieval;
* candidate depth: `20`;
* RRF constant: `60`;
* final `K = 5`.

No parameter grid, weight tuning, benchmark-specific tuning, or case-specific heuristics were used.

### Phase 1 — Measured Hybrid Benchmark

Overall RRF result:

* `Hit@5`: `0.9167`;
* `Complete@5`: `0.8333`;
* `Target Coverage@5`: `0.8750`;
* MRR: `0.7917`.

Relative to Voyage:

* `Hit@5`: unchanged;
* `Complete@5`: unchanged;
* `Target Coverage@5`: unchanged;
* MRR: `-0.0278`.

RRF repaired the semantic failure on `information_richness_cross_paper`, but it lost the semantic success on `sample_size_sensitivity_cross_paper` and did not restore the BM25-only `ml_advantage_conditions` evidence.

### Retrieval Decision

Voyage `voyage-4` is currently the strongest standalone measured retriever on the fixed benchmark.

BM25 remains valuable as a lexical baseline and exposes evidence that semantic retrieval can miss.

The evaluated RRF configuration is **not selected as the current retrieval strategy** because it matched Voyage on evidence-completeness metrics while reducing overall MRR.

The RRF implementation is retained as a tested experimental capability and audit artifact.

No further RRF parameter, candidate-depth, weight, or case-specific tuning should be performed against the current twelve-case benchmark.

The next retrieval decision must be informed by held-out evaluation.

### Phase 1 — University Thesis Requirements

The supplied ELTE Faculty of Informatics MSc/TDK dissertation guide has been converted into a canonical structured requirement set:

`config/requirements/elte_ik_msc.json`

The requirement set is pinned to the exact supplied PDF bytes using SHA-256:

`129d548384f437e2eb3b4fdee15a8471371b2b664cf86b3400b34790d12f72d5`

University constraints distinguish:

* requirement level:

  * `REQUIRED`;
  * `EXPECTED`;
  * `GUIDANCE`;

* authority:

  * `FACULTY_REQUIREMENT`;
  * `DEPARTMENT_GUIDANCE`;
  * `EIT_GUIDANCE`;
  * `GUIDE_SUMMARY`;

* scope:

  * `MSC`;
  * `EIT`;

* requirement category:

  * topic fit;
  * research;
  * method;
  * engineering;
  * novelty;
  * validation;
  * contribution;
  * independence;
  * feasibility.

The current structured requirements include:

* specialization fit;
* systematic research;
* appropriate state-of-the-art methods;
* independent research and/or engineering contribution;
* experimental software or engineering work;
* literature review alone being insufficient;
* innovation or some novelty;
* domain-appropriate validation;
* results-based contribution;
* meaningful differentiation from comparable solutions;
* independent and ethical authorship;
* EIT-specific prototype requirement;
* expected effort and thesis-length guidance.

The source does not establish a sufficiently explicit policy for permitted or restricted generative-AI assistance.

`ai-assistance-policy` therefore remains an explicit open question rather than being inferred.

### Phase 1 — University-Fit Evaluation

A deterministic university-fit decision model has been implemented.

Each applicable university requirement receives one of:

* `SATISFIED`;
* `UNSATISFIED`;
* `UNKNOWN`.

The overall university-fit states are:

* `PASS`;
* `CONCERNS`;
* `FAIL`;
* `UNKNOWN`.

Current decision semantics are:

* `REQUIRED + UNSATISFIED` → `FAIL`;
* `REQUIRED + UNKNOWN` → `UNKNOWN`;
* unsatisfied or unknown `EXPECTED` requirements → `CONCERNS`;
* `GUIDANCE` does not block approval;
* missing assessments are represented as `UNKNOWN`, never as implicit compliance;
* requirements outside the active MSc/EIT scope cannot be assessed accidentally.

The EIT-specific prototype requirement is activated only when the `EIT` scope is active.

### Phase 1 — Topic Researchability Decision Model

A structured `TopicResearchabilityReport` domain model has been implemented.

Current researchability dimensions are:

* `UNIVERSITY_FIT`;
* `LITERATURE`;
* `DATASET`;
* `BASELINES`;
* `METRICS`;
* `EXPERIMENT_FEASIBILITY`;
* `CONTRIBUTION`.

Each dimension can be:

* `PASS`;
* `CONCERNS`;
* `FAIL`;
* `UNKNOWN`.

Overall topic states are:

* `RESEARCHABLE`;
* `NOT_RESEARCHABLE`;
* `HUMAN_REVIEW_REQUIRED`;
* `UNKNOWN`.

Current aggregation semantics are:

* any failed dimension → `NOT_RESEARCHABLE`;
* otherwise, any unknown dimension → `UNKNOWN`;
* otherwise, any concern → `HUMAN_REVIEW_REQUIRED`;
* only fully known, passing dimensions → `RESEARCHABLE`.

`UNIVERSITY_FIT` is derived directly from `UniversityFitEvaluation` and cannot be manually overridden as a separate dimension.

The remaining researchability dimensions are intentionally still `UNKNOWN` until evidence-backed assessment capabilities are implemented.

### Verification

The deterministic test suite currently contains:

**128 passing tests.**

Real-system validation now includes:

* live scholarly discovery;
* live bibliographic verification;
* real Claude relevance classification;
* live OpenAlex full-text resolution;
* authenticated artifact acquisition;
* deterministic normalization of two scholarly articles;
* exact evidence addressing;
* a 212-unit multi-document retrieval corpus;
* a fixed human-reviewed evidence-target benchmark;
* repeatable BM25 evaluation;
* live Voyage embedding generation;
* in-memory semantic retrieval;
* bounded provider batching;
* bounded rate-limit handling;
* lexical-versus-semantic benchmark comparison;
* deterministic reciprocal-rank fusion;
* three-way BM25-versus-Voyage-versus-RRF evaluation;
* source-pinned MSc thesis requirements;
* deterministic university-fit evaluation;
* deterministic topic-researchability aggregation.

---

## In Progress

The first retrieval architecture comparison cycle is complete.

The university-constraints decision model is complete as a domain layer.

The next capability is:

**held-out retrieval evaluation.**

The purpose is to test whether the retrieval conclusions derived from `credit-risk-two-paper-v2` generalize to additional scholarly sources and research questions.

The existing benchmark remains unchanged as a regression benchmark.

The held-out evaluation must be defined before using its results to alter retrieval behaviour.

After retrieval has been challenged on held-out evidence, the next major research capability is evidence extraction with exact provenance.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* held-out retrieval benchmark;
* retrieval evaluation over a broader scholarly corpus;
* automated evidence extraction from retrieved passages;
* structured evidence-extraction artifacts;
* automated assessment of literature sufficiency;
* dataset availability assessment;
* baseline identification;
* evaluation-metric analysis;
* experiment-feasibility analysis;
* contribution analysis;
* research-gap analysis;
* adversarial research criticism;
* automated population of the non-university Topic Researchability dimensions;
* human approval gate for topic selection;
* claim ledger;
* neighbour/context expansion;
* explicit source-diversity-aware retrieval;
* reranking;
* vector persistence;
* normalized-document persistence;
* persistent research-artifact graph;
* orchestration framework selection;
* PDF-only scholarly-document normalization.

Later-stage work not yet started includes:

* final thesis topic selection;
* final thesis research question;
* experiment implementation;
* thesis writing;
* final academic audit.

---

## Active Decisions

### Confirmed

* Claude is the default LLM family for autonomous reasoning agents.
* LLM output is not factual evidence.
* Provider concerns should remain behind project-controlled boundaries where practical.
* Discovery, verification, relevance assessment, acquisition, normalization, retrieval, evidence extraction, and researchability evaluation are separate concerns.
* Search-planning output is not research evidence.
* The literature search planner does not formulate the final thesis research question.
* DOI verification is provider-independent.
* Missing evidence remains explicit.
* Authentication credentials are not stored in provenance.
* Raw artifacts are identified using SHA-256.
* Normalization algorithms are versioned.
* GROBID XML is preferred when a suitable machine-readable representation exists.
* Upstream document ambiguity is preserved rather than silently reconstructed.
* Evidence coordinates and evidence text are separate concepts.
* Evidence addresses include artifact identity and normalization version.
* Evidence spans are deterministically verifiable.
* One normalized paragraph is one retrieval unit in retrieval v1.
* Paragraphs are not automatically split or merged.
* Retrieval-unit identity is global across documents through artifact identity, normalization version, and paragraph ordinal.
* Section paths may contribute to retrieval representations but are not evidence text.
* BM25 is the deterministic lexical baseline.
* Semantic retrieval operates through a provider-independent embedding boundary.
* `voyage-4` is the current measured semantic baseline model.
* Cosine similarity is the current semantic ranking function.
* The current semantic index remains in memory.
* A vector database is not justified for the current corpus.
* BM25 and semantic retrieval exhibit complementary measured failure modes.
* Raw BM25 and cosine scores must not be directly added.
* Reciprocal Rank Fusion has been implemented as a deterministic experiment.
* The evaluated RRF configuration uses candidate depth `20` and constant `60`.
* The evaluated RRF configuration did not outperform Voyage semantic retrieval overall.
* The evaluated RRF configuration is not selected.
* Additional RRF tuning must not be performed against the current twelve-case benchmark.
* Voyage semantic retrieval is currently the strongest standalone measured retrieval baseline.
* The existing benchmark remains fixed as a regression benchmark.
* Held-out retrieval evaluation is required before stronger retrieval conclusions are made.
* University requirements are represented independently of topic-specific assessments.
* The supplied ELTE guide is pinned by content hash.
* University requirement level and authority are represented separately.
* Missing university-fit evidence is `UNKNOWN`, never implicit compliance.
* Required unsatisfied requirements block university fit.
* Required unknown requirements preserve an unknown decision state.
* Expected requirements can produce concerns without pretending to be hard faculty rules.
* Guidance does not act as a blocking rule.
* EIT-specific requirements are activated only under EIT scope.
* Topic researchability is multi-dimensional.
* University fit is one researchability dimension rather than the complete researchability decision.
* A topic cannot become `RESEARCHABLE` while required dimensions remain unknown.
* Concern-only outcomes require human review.
* Human approval remains required for consequential topic-selection decisions.
* Query style and retrieval scope are independent evaluation dimensions.
* Exhaustive relevance recall must not be claimed without exhaustive relevance judgements.
* Current retrieval evaluation uses explicit evidence targets with alternative acceptable anchors.
* The human-reviewed benchmark is pinned to exact artifact hashes.
* Table- and figure-associated paragraphs are not automatically excluded.
* Provider calls and retries must remain bounded.
* Agent execution must remain bounded.
* Important state is externalised into repository artifacts.
* Every pull request targeting `main` updates `CURRENT_STATE.md`.

### Not Yet Decided

* final thesis topic;
* final thesis research question;
* university policy for generative-AI assistance and disclosure;
* whether the supplied ELTE guide is the latest complete source of formal thesis policy;
* exact Claude model allocation by agent role;
* final embedding provider;
* final embedding model;
* whether lexical and semantic signals should ultimately be combined after held-out evaluation;
* whether source diversity requires an explicit retrieval mechanism;
* reranking strategy;
* context-expansion policy;
* vector database;
* persistence technology;
* orchestration framework;
* execution sandbox;
* experiment tracking system;
* observability stack;
* deployment architecture;
* final agent topology;
* final provenance persistence schema;
* final evidence-extraction schema;
* PDF parsing technology for PDF-only scholarly papers;
* whether tables and figures require future first-class document nodes;
* how large the held-out retrieval benchmark must become before retrieval architecture is sufficiently stable;
* exact evidence thresholds for each non-university researchability dimension.

---

## Current Risks

### RISK-001 — Premature architecture

Infrastructure may be introduced before requirements justify it.

**Mitigation:** continue with minimal measurable implementations and compare them against fixed benchmarks.

### RISK-002 — Model-generated false certainty

LLMs may interpret evidence more confidently than the underlying sources permit.

**Mitigation:** explicit uncertainty, exact provenance, deterministic verification, and independent auditing.

### RISK-003 — Relevance misclassification

Discovery or LLM relevance classification may be wrong.

**Mitigation:** keep discovery separate from relevance assessment and preserve uncertainty.

### RISK-004 — Incomplete scholarly metadata

Providers may expose inconsistent metadata.

**Mitigation:** preserve discrepancies and support multiple metadata registries.

### RISK-005 — Unbounded agent cost

Future autonomous loops may consume excessive calls or tokens.

**Mitigation:** explicit execution budgets and bounded fan-out.

### RISK-006 — Documentation drift

Repository documentation may fall behind runtime state.

**Mitigation:** CI-enforced `CURRENT_STATE.md` updates and executable tests as runtime authority.

### RISK-007 — Incomplete full-text availability

Relevant papers may lack accessible full text.

**Mitigation:** preserve explicit text-unavailable outcomes and avoid unbounded provider searching.

### RISK-008 — Lexical retrieval limitations

BM25 may fail when the research question and source passage use different terminology.

**Mitigation:** preserve semantic retrieval as the stronger current candidate for conceptual retrieval while retaining BM25 as a measured lexical baseline.

### RISK-009 — Document parsing fidelity

Machine-readable representations may merge or restructure publication content.

**Mitigation:** immutable raw artifact identity, normalization versioning, and preservation of upstream ambiguity.

### RISK-010 — Evidence-address instability

Normalization changes can invalidate previous paragraph or character addresses.

**Mitigation:** every address includes both artifact identity and normalization version.

### RISK-011 — Retrieval noise

Tables, appendices, repeated vocabulary, or broad semantic similarity may rank highly despite weaker evidence quality.

**Mitigation:** measure ranking behaviour before introducing filtering or reranking.

### RISK-012 — Benchmark incompleteness

The current benchmark is human-reviewed but not an exhaustive relevance judgement over every query × paragraph pair.

**Mitigation:** evaluate evidence-target satisfaction rather than claiming exhaustive paragraph recall.

### RISK-013 — Small benchmark size

The current retrieval benchmark contains only two documents and twelve queries.

**Mitigation:** treat it as a controlled regression benchmark and create held-out evaluation over additional documents and questions.

### RISK-014 — Benchmark overfitting

Repeatedly tuning retrieval logic against the same small benchmark can overfit implementation choices.

**Mitigation:** stop tuning against the original benchmark and require held-out evaluation.

### RISK-015 — Semantic concentration

Semantic retrieval may return several conceptually similar passages from one source while missing distinct evidence targets across documents.

**Mitigation:** measure this behaviour on held-out cross-document questions before adding source-diversity mechanisms.

### RISK-016 — External embedding-provider limits

Semantic retrieval depends on an external embedding API whose limits, pricing, or availability may change.

**Mitigation:** keep embedding access behind `TextEmbedder` and preserve provider substitutability.

### RISK-017 — Hybrid complexity without benefit

Hybrid retrieval can increase complexity without improving evidence retrieval.

**Evidence:** the evaluated RRF configuration matched Voyage on evidence-completeness metrics while reducing overall MRR.

**Mitigation:** do not select the current RRF hybrid or tune it against the same benchmark.

### RISK-018 — Retrieval decisions derived from development evidence

Architecture decisions may appear stronger than they are when measured only on evidence used during implementation.

**Mitigation:** require held-out retrieval evaluation before considering retrieval stable.

### RISK-019 — University-policy interpretation

The supplied dissertation guide combines faculty requirements, department/EIT guidance, summaries, links, and research resources.

**Mitigation:** preserve authority and scope explicitly in the requirement model; do not promote guidance to a faculty rule; keep unresolved policy questions explicit; verify against current formal university sources when needed.

### RISK-020 — Premature researchability approval

A candidate topic may look promising from literature availability while lacking datasets, baselines, measurable validation, feasible experiments, contribution, or university fit.

**Mitigation:** require every researchability dimension to reach an explicit state and prohibit `RESEARCHABLE` while required dimensions remain unknown or failed.

---

## Known Unknowns

The authoritative list of major unresolved project questions remains in `PROJECT.md`.

Current high-priority unknowns include:

1. Current formal university policy for generative-AI assistance and disclosure.
2. Whether the supplied ELTE dissertation guide is complete and current relative to formal faculty policy.
3. Final FinTech thesis topic.
4. Final thesis research question.
5. Dataset availability for candidate topics.
6. Baseline availability for candidate topics.
7. Suitable domain metrics and validation methods for candidate topics.
8. Experimental feasibility of candidate topics.
9. Defensible contribution or innovation for candidate topics.
10. Whether current full-text resolution provides sufficient literature coverage.
11. Whether Voyage semantic retrieval remains strongest on held-out scholarly evidence.
12. Whether lexical-semantic complementarity generalizes beyond the current two-paper benchmark.
13. Whether any hybrid strategy is justified after held-out evaluation.
14. Whether explicit source diversity is required for multi-document research questions.
15. Whether neighbouring passages should be included after retrieval.
16. Whether a dedicated reranker is necessary.
17. Whether vector persistence becomes justified as the corpus grows.
18. How tables, figures, equations, and non-prose evidence should eventually be represented.
19. How PDF-only scholarly papers should be normalized.
20. How large the held-out retrieval benchmark must become before retrieval architecture is considered sufficiently stable.
21. Which persistence representation should eventually store source → artifact → document → retrieval → evidence → claim relationships.

---

## Next Actions

1. Merge the university-constraints and topic-researchability domain slice.
2. Preserve `credit-risk-two-paper-v2` unchanged as the original retrieval regression benchmark.
3. Do not tune RRF or other retrieval mechanisms against the original twelve-case benchmark.
4. Design a held-out retrieval evaluation using additional scholarly documents and research questions.
5. Freeze the held-out documents, questions, evidence targets, and acceptable anchors before system comparison.
6. Evaluate BM25 and Voyage against the held-out set.
7. Use held-out results to determine whether the current retrieval strategy is sufficiently stable for evidence extraction.
8. Reconsider hybrid retrieval only if held-out evidence demonstrates a repeatable need.
9. Begin evidence extraction with exact paragraph/character provenance.
10. Use extracted evidence to implement the remaining researchability assessors:

* literature sufficiency;
* dataset availability;
* baselines;
* metrics;
* experiment feasibility;
* contribution and research-gap evidence.

11. Preserve unknowns instead of coercing incomplete evidence into pass/fail decisions.
12. Add the explicit human approval gate only after the structured report can be populated from evidence.

---

## Current Milestone Exit Criteria

The initial Topic Researchability milestone is complete when:

* candidate topics can drive bounded scholarly search planning;
* planned searches drive scholarly discovery;
* duplicate discoveries are consolidated with provenance;
* sources are bibliographically verified;
* relevance is assessed with explicit uncertainty;
* usable full text is resolved where available;
* retrieved artifacts have immutable identities;
* scholarly documents are deterministically normalized;
* exact evidence spans are addressable and independently verifiable;
* multi-document evidence retrieval operates without sending entire papers to an LLM;
* retrieval behaviour is evaluated against fixed evidence requirements;
* lexical and semantic retrieval behaviour is understood empirically;
* retrieval conclusions have been challenged on held-out evidence;
* the selected retrieval strategy is justified by measured evidence rather than convention;
* university thesis constraints are represented explicitly with authority and scope;
* university fit can be evaluated without silently treating missing evidence as compliance;
* relevant evidence can be extracted with exact provenance;
* research gaps can be evaluated adversarially;
* datasets, baselines, metrics, and experimental feasibility can be assessed;
* contribution can be assessed against university expectations;
* every researchability dimension has an explicit epistemic state;
* unresolved questions remain explicit;
* a human can approve, reject, or request further investigation;
* the complete decision path is auditable from repository artifacts.