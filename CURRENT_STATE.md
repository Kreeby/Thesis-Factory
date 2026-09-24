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
* frozen held-out retrieval evaluation;
* lexical-versus-semantic-versus-hybrid retrieval comparison;
* source-pinned university thesis requirements;
* deterministic university-fit evaluation;
* structured topic-researchability decision state.

The retrieval architecture comparison cycle is now complete for Phase 1.

The original development benchmark and an independently frozen held-out benchmark both show that Voyage `voyage-4` semantic retrieval is the strongest standalone measured retriever among the evaluated systems.

The evaluated Reciprocal Rank Fusion configuration does not improve evidence completeness or target coverage over Voyage and reduces MRR on both development and held-out evaluation. It is therefore retained only as an audited negative experiment.

Voyage `voyage-4` is selected as the default retrieval strategy for the next Phase 1 evidence-acquisition work. BM25 remains the deterministic lexical baseline and diagnostic comparator.

University thesis requirements from the supplied ELTE Faculty of Informatics dissertation guide are represented explicitly, and topic researchability can represent university fit together with literature, dataset, baseline, metric, experiment-feasibility, and contribution dimensions while preserving unresolved dimensions as `UNKNOWN`.

The next major technical objective is **evidence acquisition with exact provenance**.

---

## Current Objective

Build the first evidence-acquisition slice on top of the now-selected retrieval baseline.

The target flow is:

`research question / assessment need`

→ bounded evidence requirements

→ bounded retrieval queries

→ Voyage semantic retrieval

→ deterministic context expansion

→ evidence-span proposal

→ deterministic evidence-span verification

→ structured evidence artifacts

The retrieval stage must remain separate from evidence extraction.

The selected retriever supplies candidate paragraphs; it does not decide whether a factual claim is supported.

Context expansion must remain separate from ranking and retrieval-unit identity. A retrieved paragraph remains the canonical retrieval hit even when neighbouring paragraphs are supplied as additional extraction context.

The immediate evidence-acquisition work should preserve:

* exact artifact identity;
* normalization-version identity;
* paragraph-level retrieval identity;
* deterministic character-span addressing;
* bounded query fan-out;
* bounded context expansion;
* explicit `UNKNOWN` outcomes when evidence is insufficient;
* no unbounded provider chasing;
* no new retrieval tuning against the frozen benchmarks;
* no LLM-generated factual claim treated as evidence without deterministic source verification.

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
* Source identity verification implemented with explicit `CONFIRMED`, `CONFLICTING`, and `INSUFFICIENT_DATA` states.
* Verification discrepancies are preserved rather than hidden.
* Source verification can operate independently on an already discovered source.
* `discover_and_verify_sources` workflow implemented.
* DataCite fallback was verified against an arXiv DOI not resolved through Crossref.

### Phase 1 — LLM Reasoning Boundary

* Provider-independent structured LLM reasoning boundary implemented.
* Anthropic / Claude structured reasoning adapter implemented.
* Claude-backed scholarly source relevance assessment implemented.
* Relevance assessment uses explicit `RELEVANT`, `NOT_RELEVANT`, `UNCERTAIN`, and `INSUFFICIENT_EVIDENCE` states.
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
* Supported location representations include OpenAlex GROBID XML, OpenAlex cached PDF, original open-access PDF, and scholarly landing page.
* Locations are deduplicated.
* Landing pages are not treated as downloadable full text.
* Preferred text-location order is OpenAlex GROBID XML → OpenAlex cached PDF → original open-access PDF.
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

A real OpenAlex GROBID artifact for `Corporate default forecasting with machine learning` was downloaded with:

* OpenAlex work: `W3010059221`;
* size: `234692` bytes;
* SHA-256: `ae21bed28e5f9ab69878493e474bb41537621bebe692018944ed1cc2311d1d67`.

### Phase 1 — Scholarly Document Normalization

* `NormalizedDocument`, `NormalizedSection`, and `NormalizedParagraph` implemented.
* Current normalization version is `grobid-tei-v1`.
* GROBID TEI parser implemented using hardened XML parsing.
* Standard GROBID TEI and legacy OpenAlex GROBID forms are supported.
* Namespace differences are handled.
* Title, abstract, sections, nested paths, paragraphs, and available `xml:id` values are preserved.
* Paragraph whitespace is normalized deterministically.
* Section and paragraph ordinals are deterministic and unique within a document.
* Section heading roles are represented separately from section content type.
* Current heading roles are `STANDARD`, `TABLE`, and `FIGURE`.
* Table- or figure-like headings do not cause all contained paragraphs to be treated as non-prose.
* Upstream GROBID structural ambiguities are preserved rather than heuristically repaired.

Real normalization of `W3010059221` produced 25 sections and 119 paragraphs.

`Enhancing Credit Scoring with Alternative Data` (`W3044323082`) was also normalized successfully, producing 20 sections and 93 paragraphs with artifact SHA-256 `640d703f9028b31a6ed1336b8deb38261a93cad81957616972ed8041ba3cf034`.

A held-out document with artifact SHA-256 `b674fc01eb85313a75f8670e0c5e2d6b74da9b1d7b3d65b8494437786dfe3757` normalized successfully but did not expose a document title through the current GROBID title-extraction path. Source metadata still identifies the work. This is a parsing-fidelity observation, not a retrieval blocker.

### Phase 1 — Stable Evidence Addressing

* `EvidenceAddress` implemented.
* `EvidenceSpan` implemented.
* Evidence addresses contain artifact SHA-256, normalization version, paragraph ordinal, zero-based start character offset, and zero-based exclusive end character offset.
* Character spans use `[start_char, end_char)` semantics.
* Evidence coordinates and evidence text are separate concepts.
* Evidence text is deterministically resolved from the normalized document.
* Wrong artifact identities, normalization versions, paragraph ordinals, and character ranges are rejected.
* Evidence can be independently re-resolved and verified.
* Fabricated or modified evidence text fails deterministic verification.

A live evidence diagnostic successfully resolved and verified an exact passage from paragraph 102 of `W3010059221`.

### Phase 1 — Retrieval Units and Multi-Document Corpus

Paragraph-size distribution was measured on real scholarly text before choosing a retrieval unit.

For `W3010059221`:

* 119 paragraphs;
* median: 372 characters / 62 words;
* P95: 1337 characters / 209 words;
* maximum: 2377 characters / 399 words.

This supported the retrieval-v1 decision:

`one NormalizedParagraph = one RetrievalUnit`

No automatic paragraph splitting or merging is performed.

`RetrievalUnit` and globally unique `RetrievalUnitId` are implemented. Retrieval identity uses artifact SHA-256, normalization version, and paragraph ordinal. Section paths may contribute to retrieval representations but do not become evidence text.

The development benchmark corpus contains 2 scholarly documents and 212 retrieval units.

The held-out benchmark corpus contains 4 scholarly documents and 227 retrieval units.

### Phase 1 — BM25 Retrieval Baseline

* Dependency-free deterministic BM25 lexical retrieval implemented.
* BM25 indexing uses section path plus paragraph text.
* Original paragraph text remains unchanged.
* Search is case-insensitive.
* Zero-score units are excluded.
* Ranking ties are deterministic.
* Caller specifies bounded `top_k`.

BM25 remains the deterministic lexical baseline and diagnostic comparator.

### Phase 1 — Semantic Retrieval Baseline

* Provider-independent `TextEmbedder` protocol implemented.
* In-memory `SemanticRetriever` implemented.
* Semantic retrieval operates over the same canonical `RetrievalUnit` corpus as BM25.
* Document embedding text contains section path plus exact normalized paragraph text.
* Semantic ranking uses cosine similarity.
* Query and document embeddings remain separate operations.
* No vector database is required for the currently measured corpus sizes.

### Phase 1 — Voyage Embedding Integration

* Voyage AI embedding integration implemented behind the project-controlled embedding boundary.
* Current semantic model: `voyage-4`.
* Queries use Voyage `query` input type.
* Retrieval units use Voyage `document` input type.
* Silent provider-side text truncation is disabled.
* Provider responses are validated for count, indices, dimensions, and finite values.
* Embeddings are restored to caller order using provider response indices.
* Document embedding requests are bounded into batches.
* Retryable provider failures use bounded retry.
* `Retry-After` is respected when available.
* Exponential backoff is bounded.
* Request pacing is configurable.
* Current defaults are compatible with the no-payment-method development limits used during evaluation: batch size `24`, minimum request interval `21` seconds.
* No API credentials are persisted in project artifacts or provenance.

### Phase 1 — Retrieval Evaluation Framework

* Generic `Retriever` protocol implemented.
* Retrieval evaluation is independent of BM25, semantic, and hybrid implementations.
* Query style and evaluation scope are represented independently.
* Query styles: `LEXICAL`, `PARAPHRASE`.
* Scopes: `SINGLE_DOCUMENT`, `SOURCE_SELECTION`, `CROSS_DOCUMENT`.
* Evaluation uses explicit evidence targets rather than pretending to have exhaustive relevance judgements.
* Each `RetrievalTarget` describes one evidence requirement and one or more acceptable passage anchors.

Current metrics are:

* `Hit@K`;
* `Complete@K`;
* `Target Coverage@K`;
* reciprocal rank;
* MRR.

### Phase 1 — Development Retrieval Benchmark

Persistent benchmark:

`evals/retrieval/baseline_v2.json`

Benchmark name:

`credit-risk-two-paper-v2`

It contains:

* 2 pinned scholarly documents;
* 212 retrieval units;
* 12 human-reviewed research queries;
* 16 evidence targets;
* lexical and paraphrased queries;
* single-document, source-selection, and cross-document questions.

At `K = 5`:

#### BM25

* `Hit@5`: `0.9167`;
* `Complete@5`: `0.7500`;
* `Target Coverage@5`: `0.8333`;
* MRR: `0.6319`.

#### Voyage `voyage-4`

* `Hit@5`: `0.9167`;
* `Complete@5`: `0.8333`;
* `Target Coverage@5`: `0.8750`;
* MRR: `0.8194`.

#### RRF hybrid

Configuration:

* BM25 + Voyage `voyage-4`;
* candidate depth: `20`;
* RRF constant: `60`;
* final `K = 5`.

Result:

* `Hit@5`: `0.9167`;
* `Complete@5`: `0.8333`;
* `Target Coverage@5`: `0.8750`;
* MRR: `0.7917`.

Development evidence showed lexical and semantic complementarity, but the evaluated RRF configuration did not outperform Voyage overall.

### Phase 1 — Frozen Held-Out Retrieval Benchmark

A second benchmark was constructed specifically to challenge the development conclusions without tuning against the result.

Persistent benchmark:

`evals/retrieval/held_out_v1.json`

Benchmark name:

`credit-risk-four-paper-held-out-v1`

The benchmark was frozen at commit:

`61e2c82`

before BM25, Voyage, or RRF were evaluated against its cases.

Selection used four fixed OpenAlex semantic-discovery strata:

* consumer credit scoring machine learning;
* corporate default prediction machine learning;
* alternative data credit scoring;
* explainable machine learning credit risk.

The two development-benchmark DOI identities were explicitly excluded during held-out source selection.

The frozen held-out benchmark contains:

* 4 previously unseen scholarly documents;
* 227 retrieval units;
* 12 cases;
* 16 evidence targets;
* 5 lexical cases;
* 7 paraphrase cases;
* 8 single-document cases;
* 2 source-selection cases;
* 2 cross-document cases.

Pinned held-out artifacts:

* `b674fc01eb85313a75f8670e0c5e2d6b74da9b1d7b3d65b8494437786dfe3757` — OpenAlex `W4411246912`;
* `84125ef740441a8237bf166e584f327ecb6175d2a5a8d754b5e85c78aa2da804` — OpenAlex `W3047063927`;
* `44b3f8d6dd1e93dc796d1a989d3dd75c92850b364d67590c633348373b942a8e` — OpenAlex `W4411067263`;
* `0a8a371851257a08bdae408b8c4170bf621c6bfba7bcb0e8ee4f7b543657a46f` — OpenAlex `W3000463950`.

### Phase 1 — Held-Out Retrieval Results

All held-out results below use the frozen benchmark and `K = 5`.

#### Overall

BM25:

* `Hit@5`: `0.8333`;
* `Complete@5`: `0.5833`;
* `Target Coverage@5`: `0.7083`;
* MRR: `0.6875`.

Voyage `voyage-4`:

* `Hit@5`: `0.9167`;
* `Complete@5`: `0.7500`;
* `Target Coverage@5`: `0.8333`;
* MRR: `0.8125`.

RRF hybrid:

* `Hit@5`: `0.9167`;
* `Complete@5`: `0.7500`;
* `Target Coverage@5`: `0.8333`;
* MRR: `0.7569`.

#### By query style

Lexical cases:

* BM25: `Hit@5 1.0000`, `Complete@5 1.0000`, `Coverage 1.0000`, `MRR 0.9000`;
* Voyage: `Hit@5 1.0000`, `Complete@5 1.0000`, `Coverage 1.0000`, `MRR 0.7500`;
* RRF: `Hit@5 1.0000`, `Complete@5 1.0000`, `Coverage 1.0000`, `MRR 0.7667`.

Paraphrase cases:

* BM25: `Hit@5 0.7143`, `Complete@5 0.2857`, `Coverage 0.5000`, `MRR 0.5357`;
* Voyage: `Hit@5 0.8571`, `Complete@5 0.5714`, `Coverage 0.7143`, `MRR 0.8571`;
* RRF: `Hit@5 0.8571`, `Complete@5 0.5714`, `Coverage 0.7143`, `MRR 0.7500`.

#### By scope

Single-document cases:

* BM25: `Hit@5 0.7500`, `Complete@5 0.6250`, `Coverage 0.6875`, `MRR 0.6875`;
* Voyage: `Hit@5 0.8750`, `Complete@5 0.7500`, `Coverage 0.8125`, `MRR 0.7188`;
* RRF: `Hit@5 0.8750`, `Complete@5 0.7500`, `Coverage 0.8125`, `MRR 0.6354`.

Source-selection cases:

* all three systems: `Hit@5 1.0000`, `Complete@5 1.0000`, `Coverage 1.0000`;
* BM25 MRR: `0.6250`;
* Voyage MRR: `1.0000`;
* RRF MRR: `1.0000`.

Cross-document cases:

* BM25: `Hit@5 1.0000`, `Complete@5 0.0000`, `Coverage 0.5000`, `MRR 0.7500`;
* Voyage: `Hit@5 1.0000`, `Complete@5 0.5000`, `Coverage 0.7500`, `MRR 1.0000`;
* RRF: `Hit@5 1.0000`, `Complete@5 0.5000`, `Coverage 0.7500`, `MRR 1.0000`.

### Phase 1 — Held-Out Observations

The held-out benchmark reproduced the main development pattern:

* Voyage materially outperformed BM25 on paraphrased evidence needs;
* BM25 remained strong on explicit lexical questions;
* RRF matched Voyage on held-out hit/completeness/coverage but again reduced overall MRR;
* cross-document evidence completeness remained a harder problem than source selection;
* no held-out result justified another round of RRF tuning.

Measured examples also exposed the next architecture bottleneck.

`consumer_imbalanced_metrics`:

* BM25 found no frozen target;
* Voyage recovered both frozen evidence targets;
* RRF also recovered both but ranked the first acceptable evidence later.

`pca_accuracy_tradeoff`:

* all systems achieved only `0.5` target coverage;
* retrieved passages landed in the correct local region of the document;
* adjacent-paragraph evidence is therefore a concrete motivation for bounded context expansion rather than another retriever change.

`xai_local_global_explanations`:

* all systems missed the frozen acceptable anchor in the top five;
* top results remained in the correct conceptual section;
* this supports decomposing broad research questions into bounded evidence requirements before retrieval/extraction rather than requiring one ranking to satisfy every facet directly.

`rare_defaults_cross_paper`:

* BM25 recovered only one of two targets;
* Voyage and RRF recovered both targets;
* semantic retrieval therefore improved cross-document completeness on at least one independent held-out case.

`interpretability_cross_paper`:

* all three systems recovered only the XAI-side target;
* explicit source-diversity machinery is not yet selected because bounded evidence-requirement decomposition should be evaluated first.

### Phase 1 — Retrieval Decision v1

The retrieval evidence now supports a Phase 1 selection rather than only a provisional baseline.

**Selected default retrieval strategy v1: Voyage `voyage-4` semantic retrieval.**

Reasons:

* it had the strongest standalone development-benchmark result;
* it remained the strongest standalone retriever on the independently frozen held-out benchmark;
* it materially improved paraphrase retrieval on both benchmark families;
* it improved held-out completeness and target coverage relative to BM25;
* it matched or exceeded the evaluated RRF hybrid on evidence-completeness metrics while retaining higher overall MRR.

BM25 remains:

* the deterministic lexical baseline;
* a diagnostic comparator;
* useful evidence that semantic retrieval does not dominate every individual lexical ranking problem.

The evaluated RRF configuration remains:

* implemented;
* tested;
* reproducible;
* retained in the audit trail;
* **not selected** for production retrieval v1.

No further RRF constant, candidate-depth, weighting, or benchmark-specific tuning is justified at this stage.

The current retrieval architecture is sufficiently validated to proceed to evidence acquisition.

### Phase 1 — University Thesis Requirements

The supplied ELTE Faculty of Informatics MSc/TDK dissertation guide is represented in:

`config/requirements/elte_ik_msc.json`

The requirement set is pinned to source SHA-256:

`129d548384f437e2eb3b4fdee15a8471371b2b664cf86b3400b34790d12f72d5`

University constraints distinguish requirement level, authority, scope, and category.

Current requirement levels:

* `REQUIRED`;
* `EXPECTED`;
* `GUIDANCE`.

Current authorities:

* `FACULTY_REQUIREMENT`;
* `DEPARTMENT_GUIDANCE`;
* `EIT_GUIDANCE`;
* `GUIDE_SUMMARY`.

Current scopes:

* `MSC`;
* `EIT`.

The current structured requirements cover specialization fit, systematic research, methods, independent engineering/research contribution, experimental work, literature-review insufficiency, innovation/novelty, validation, results-based contribution, differentiation, independent/ethical authorship, EIT prototype expectations, and effort/length guidance.

The supplied source does not establish a sufficiently explicit generative-AI assistance policy. `ai-assistance-policy` therefore remains an explicit open question.

### Phase 1 — University-Fit Evaluation

A deterministic university-fit decision model is implemented.

Each applicable requirement receives `SATISFIED`, `UNSATISFIED`, or `UNKNOWN`.

Overall university-fit states are `PASS`, `CONCERNS`, `FAIL`, and `UNKNOWN`.

Decision semantics:

* `REQUIRED + UNSATISFIED` → `FAIL`;
* `REQUIRED + UNKNOWN` → `UNKNOWN`;
* unsatisfied or unknown `EXPECTED` requirements → `CONCERNS`;
* `GUIDANCE` does not block approval;
* missing assessments are `UNKNOWN` rather than implicit compliance;
* requirements outside the active MSc/EIT scope cannot be assessed accidentally.

The EIT-specific prototype requirement activates only when the `EIT` scope is active.

### Phase 1 — Topic Researchability Decision Model

`TopicResearchabilityReport` is implemented.

Current dimensions:

* `UNIVERSITY_FIT`;
* `LITERATURE`;
* `DATASET`;
* `BASELINES`;
* `METRICS`;
* `EXPERIMENT_FEASIBILITY`;
* `CONTRIBUTION`.

Each dimension can be `PASS`, `CONCERNS`, `FAIL`, or `UNKNOWN`.

Overall topic states:

* `RESEARCHABLE`;
* `NOT_RESEARCHABLE`;
* `HUMAN_REVIEW_REQUIRED`;
* `UNKNOWN`.

Aggregation semantics:

* any failed dimension → `NOT_RESEARCHABLE`;
* otherwise, any unknown dimension → `UNKNOWN`;
* otherwise, any concern → `HUMAN_REVIEW_REQUIRED`;
* only fully known, passing dimensions → `RESEARCHABLE`.

`UNIVERSITY_FIT` is derived from `UniversityFitEvaluation` and cannot be manually overridden as a separate dimension.

The non-university researchability dimensions intentionally remain `UNKNOWN` until evidence-backed assessors are implemented.

### Verification

The deterministic test suite currently contains:

**132 passing tests.**

Real-system validation now includes:

* live scholarly discovery;
* live bibliographic verification;
* real Claude relevance classification;
* live OpenAlex full-text resolution;
* authenticated artifact acquisition;
* deterministic scholarly normalization;
* exact evidence addressing;
* development retrieval corpus and benchmark;
* live Voyage embedding generation;
* bounded provider batching and rate-limit handling;
* BM25, Voyage, and deterministic RRF evaluation;
* a frozen four-paper held-out benchmark committed before retrieval evaluation;
* held-out BM25-versus-Voyage-versus-RRF comparison;
* source-pinned MSc thesis requirements;
* deterministic university-fit evaluation;
* deterministic topic-researchability aggregation.

---

## In Progress

The retrieval architecture comparison cycle is complete for the current Phase 1 scope.

The default retrieval strategy v1 is selected:

**Voyage `voyage-4` semantic retrieval.**

The current in-progress capability is:

**evidence acquisition with exact provenance.**

The first evidence-acquisition slice should define the contract between a research need and verifiable evidence without prematurely implementing the entire researchability pipeline.

The immediate design target is:

* explicit evidence requirements;
* bounded retrieval-query planning;
* selected semantic retrieval;
* bounded deterministic neighbour/context expansion;
* exact evidence-span extraction;
* deterministic span verification.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* `EvidenceRequirement` domain model;
* bounded evidence-query planning;
* neighbour/context expansion;
* Claude-backed evidence extraction from bounded retrieved context;
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
* persistent research-artifact graph;
* normalized-document persistence;
* vector persistence;
* orchestration framework selection;
* PDF-only scholarly-document normalization.

Potential retrieval capabilities intentionally **not selected for immediate work** include:

* explicit source-diversity reranking;
* dedicated LLM reranking;
* additional RRF tuning;
* weighted lexical-semantic fusion.

These should be introduced only if later evidence-acquisition evaluation demonstrates a measured need.

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
* Paragraphs are not automatically split or merged for ranking.
* Retrieval-unit identity is global across documents through artifact identity, normalization version, and paragraph ordinal.
* Section paths may contribute to retrieval representations but are not evidence text.
* BM25 is the deterministic lexical baseline.
* Semantic retrieval operates through a provider-independent embedding boundary.
* Voyage `voyage-4` is the selected default retrieval strategy v1 for evidence acquisition.
* Cosine similarity is the current semantic ranking function.
* The current semantic index remains in memory.
* A vector database is not justified for the currently measured corpus sizes.
* BM25 and semantic retrieval exhibit complementary measured failure modes.
* Voyage materially outperforms BM25 on measured paraphrase retrieval.
* Raw BM25 and cosine scores must not be directly added.
* Reciprocal Rank Fusion is implemented as a deterministic experiment.
* The evaluated RRF configuration uses candidate depth `20` and constant `60`.
* The evaluated RRF configuration did not outperform Voyage on either development or held-out evaluation.
* The evaluated RRF configuration is not selected for retrieval v1.
* Additional RRF tuning against the existing benchmarks is not justified.
* `credit-risk-two-paper-v2` remains fixed as the development/regression benchmark.
* `credit-risk-four-paper-held-out-v1` remains frozen at commit `61e2c82`.
* The held-out benchmark was fixed before retrieval evaluation.
* Held-out evaluation confirmed the major development conclusion that Voyage is the strongest standalone measured retriever among the evaluated systems.
* Held-out evaluation also confirmed that lexical questions can still rank better under BM25.
* Context expansion must remain separate from ranking and retrieval-unit identity.
* Broad multi-facet research questions should be decomposed into bounded evidence requirements rather than relying on one ranking to satisfy every facet.
* Explicit source-diversity machinery is not selected before evidence-requirement decomposition is evaluated.
* Retrieval quality must be measured before architectural escalation.
* Query style and retrieval scope are independent evaluation dimensions.
* Exhaustive relevance recall must not be claimed without exhaustive relevance judgements.
* Retrieval evaluation uses explicit evidence targets with alternative acceptable anchors.
* Benchmarks are pinned to exact artifact hashes.
* Table- and figure-associated paragraphs are not automatically excluded.
* Provider calls and retries must remain bounded.
* Agent execution must remain bounded.
* University requirements are represented independently of topic-specific assessments.
* The supplied ELTE guide is pinned by content hash.
* University requirement level and authority are represented separately.
* Missing university-fit evidence is `UNKNOWN`, never implicit compliance.
* Required unsatisfied requirements block university fit.
* Required unknown requirements preserve an unknown decision state.
* Expected requirements can produce concerns without pretending to be hard faculty rules.
* Guidance does not act as a blocking rule.
* EIT-specific requirements activate only under EIT scope.
* Topic researchability is multi-dimensional.
* University fit is one researchability dimension rather than the complete researchability decision.
* A topic cannot become `RESEARCHABLE` while required dimensions remain unknown.
* Concern-only outcomes require human review.
* Human approval remains required for consequential topic-selection decisions.
* Important state is externalised into repository artifacts.
* Every pull request targeting `main` updates `CURRENT_STATE.md`.

### Not Yet Decided

* final thesis topic;
* final thesis research question;
* university policy for generative-AI assistance and disclosure;
* whether the supplied ELTE guide is the latest complete source of formal thesis policy;
* exact Claude model allocation by agent role;
* long-term embedding provider and model beyond the current retrieval-v1 selection;
* exact evidence-requirement schema;
* exact bounded query-planning contract;
* context-expansion radius and boundary rules;
* whether context expansion should remain within a section or may cross section boundaries;
* exact evidence-extraction artifact schema;
* evidence sufficiency thresholds for non-university researchability dimensions;
* whether explicit source diversity is necessary after evidence-requirement decomposition;
* whether a dedicated reranker becomes necessary later;
* vector database;
* persistence technology;
* orchestration framework;
* execution sandbox;
* experiment tracking system;
* observability stack;
* deployment architecture;
* final agent topology;
* final provenance persistence schema;
* PDF parsing technology for PDF-only scholarly papers;
* whether tables and figures require future first-class document nodes.

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

**Evidence:** development and held-out paraphrase evaluations both materially favoured Voyage over BM25.

**Mitigation:** use Voyage semantic retrieval as retrieval v1 while retaining BM25 as a lexical diagnostic baseline.

### RISK-009 — Document parsing fidelity

Machine-readable representations may merge, omit, or restructure publication content or metadata.

**Evidence:** one held-out GROBID artifact normalized successfully but yielded no parsed document title.

**Mitigation:** immutable raw artifact identity, normalization versioning, source metadata retention, and preservation of upstream ambiguity.

### RISK-010 — Evidence-address instability

Normalization changes can invalidate previous paragraph or character addresses.

**Mitigation:** every evidence address includes both artifact identity and normalization version.

### RISK-011 — Retrieval noise

Tables, appendices, repeated vocabulary, or broad semantic similarity may rank highly despite weaker evidence quality.

**Mitigation:** separate candidate retrieval from evidence extraction and verify exact supporting spans deterministically.

### RISK-012 — Benchmark incompleteness

The retrieval benchmarks are human-reviewed but do not contain exhaustive relevance judgements over every query × paragraph pair.

**Mitigation:** evaluate explicit evidence-target satisfaction rather than claiming exhaustive paragraph recall.

### RISK-013 — Limited benchmark scale

The development benchmark contains two documents and twelve cases; the held-out benchmark adds four documents and twelve independent cases but still does not establish universal retrieval quality.

**Mitigation:** treat the combined evidence as sufficient for the current Phase 1 retrieval-v1 selection, not as a universal model ranking.

### RISK-014 — Benchmark overfitting

Repeatedly tuning against fixed benchmarks can convert evaluation sets into development targets.

**Mitigation:** the held-out benchmark was frozen before evaluation; do not tune retrieval parameters, anchors, or query-specific behaviour against either existing benchmark.

### RISK-015 — Multi-facet and cross-document evidence incompleteness

A single query can retrieve a conceptually correct region while failing to satisfy every evidence facet or source requirement.

**Evidence:** `pca_accuracy_tradeoff`, `xai_local_global_explanations`, and `interpretability_cross_paper` remained incomplete despite relevant nearby or same-section retrievals.

**Mitigation:** introduce bounded evidence-requirement decomposition and deterministic context expansion before adding source-diversity or reranking machinery.

### RISK-016 — External embedding-provider limits

Semantic retrieval depends on an external embedding API whose limits, pricing, or availability may change.

**Mitigation:** keep embedding access behind `TextEmbedder`, use bounded batching/retry/pacing, and preserve provider substitutability.

### RISK-017 — Hybrid complexity without benefit

Hybrid retrieval can increase complexity without improving evidence retrieval.

**Evidence:** on both development and held-out benchmarks, the evaluated RRF configuration matched Voyage on key completeness metrics while reducing overall MRR.

**Mitigation:** do not select or tune the current RRF hybrid.

### RISK-018 — Retrieval decisions derived from development evidence

This risk has been materially reduced by a frozen held-out evaluation but not eliminated by the small corpus size.

**Mitigation:** preserve the held-out benchmark and freeze boundary, avoid retrospective anchor changes, and treat retrieval v1 as a scoped Phase 1 decision rather than a universal conclusion.

### RISK-019 — University-policy interpretation

The supplied dissertation guide combines faculty requirements, department/EIT guidance, summaries, links, and research resources.

**Mitigation:** preserve authority and scope explicitly; do not promote guidance to faculty policy; keep unresolved policy questions explicit; verify against current formal university sources when needed.

### RISK-020 — Premature researchability approval

A candidate topic may look promising from literature availability while lacking datasets, baselines, measurable validation, feasible experiments, contribution, or university fit.

**Mitigation:** require every researchability dimension to reach an explicit state and prohibit `RESEARCHABLE` while required dimensions remain unknown or failed.

### RISK-021 — Context expansion can blur evidence identity

Adding neighbouring paragraphs for interpretation can accidentally make retrieval context look like independently retrieved evidence.

**Mitigation:** preserve the original retrieval-hit identity separately, represent context explicitly, and require final extracted evidence to resolve to exact paragraph/character coordinates.

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
10. Whether current full-text resolution provides sufficient literature coverage for future candidate topics.
11. Exact schema for a bounded `EvidenceRequirement`.
12. How many retrieval queries an evidence requirement may generate.
13. How neighbouring paragraphs should be expanded around a retrieval hit.
14. Whether context expansion may cross section boundaries.
15. How evidence extraction should represent `SUPPORTED`, `PARTIAL`, `CONTESTED`, or insufficient-evidence outcomes, if such states are introduced.
16. Exact structured artifact linking evidence requirements, retrieval hits, expanded context, and verified `EvidenceSpan` objects.
17. Whether explicit source diversity is still necessary after evidence-requirement decomposition.
18. Whether a dedicated reranker becomes necessary after evidence-acquisition evaluation.
19. Whether vector persistence becomes justified as the corpus grows.
20. How tables, figures, equations, and non-prose evidence should eventually be represented.
21. How PDF-only scholarly papers should be normalized.
22. Which persistence representation should eventually store source → artifact → document → retrieval → evidence → claim relationships.

---

## Next Actions

1. Merge the held-out retrieval slice with the frozen benchmark, evaluation runner, measured results, and this updated `CURRENT_STATE.md`.
2. Preserve `credit-risk-two-paper-v2` as the development/regression benchmark.
3. Preserve `credit-risk-four-paper-held-out-v1` unchanged at freeze commit `61e2c82`.
4. Do not tune Voyage, BM25, RRF, candidate depth, fusion weights, or benchmark-specific behaviour against the existing benchmarks.
5. Start `phase1/evidence-acquisition` after the held-out PR is merged.
6. Define the minimal `EvidenceRequirement` domain model before introducing a new agent abstraction.
7. Define bounded evidence-query planning separately from final research-question formulation.
8. Use Voyage `voyage-4` as the default candidate retriever.
9. Add deterministic neighbour/context expansion without changing canonical retrieval-hit identity.
10. Add Claude-backed evidence-span proposal over bounded retrieved context.
11. Re-resolve and verify every proposed `EvidenceSpan` deterministically against the normalized document.
12. Persist structured evidence-extraction output before using it to populate researchability dimensions.
13. Evaluate evidence acquisition on fixed evidence requirements before adding reranking, diversity, or persistence infrastructure.
14. Preserve unknowns instead of coercing incomplete evidence into pass/fail decisions.
15. Add the explicit human approval gate only after the structured Topic Researchability report can be populated from verified evidence.

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
