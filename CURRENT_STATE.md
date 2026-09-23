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
* multi-document paragraph retrieval;
* deterministic BM25 lexical ranking;
* human-reviewed retrieval benchmarking.

The project is now moving from a measured lexical retrieval baseline toward semantic retrieval comparison.

---

## Current Objective

Determine whether semantic retrieval materially improves evidence retrieval over the current BM25 baseline, especially for paraphrased and cross-document research questions.

The next retrieval implementation must be evaluated against the same fixed benchmark rather than against ad-hoc examples.

The current baseline deliberately does not use:

* embeddings;
* vector databases;
* semantic reranking;
* LLM reranking;
* automatic paragraph merging;
* automatic paragraph splitting.

This provides a transparent deterministic baseline against which later retrieval capabilities can be measured.

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

### Phase 1 — Retrieval Evaluation Framework

* Generic `Retriever` protocol implemented.
* Retrieval evaluation is independent of BM25 and can be reused for future semantic and hybrid retrievers.
* Query style and evaluation scope are represented as separate dimensions.

Current query styles:

* `LEXICAL`;
* `PARAPHRASE`.

Current scopes:

* `SINGLE_DOCUMENT`;
* `SOURCE_SELECTION`;
* `CROSS_DOCUMENT`.

The initial exhaustive relevance-list approach was rejected after audit because the benchmark did not contain complete relevance judgements for all 212 passages.

The evaluation model was changed to evidence targets.

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

A persistent benchmark has been created:

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

BM25 output was not treated as exhaustive ground truth.

The benchmark therefore evaluates whether retrieval supplies evidence sufficient to satisfy explicit research requirements rather than pretending that every relevant paragraph has been exhaustively labelled.

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

### Observed BM25 Failure Modes

The benchmark exposes specific measured weaknesses rather than hypothetical ones.

#### Paraphrase failure

For:

`combined_nontraditional_predictors`

BM25 returned no acceptable evidence anchor in the top five results.

Result:

* `Hit@5 = false`;
* `Complete@5 = false`;
* `Target Coverage@5 = 0`.

#### Multi-facet paraphrase failure

For:

`ml_advantage_conditions`

BM25 found evidence related to rich information but failed to recover the separate small-training-set evidence target.

Result:

* target coverage: `0.5`;
* complete: `false`.

#### Cross-document evidence-completeness failure

For:

`sample_size_sensitivity_cross_paper`

BM25 found evidence from the alternative-data paper but failed to retrieve the required corporate-default evidence target.

Result:

* target coverage: `0.5`;
* complete: `false`.

#### Ranking noise

For a direct machine-learning-algorithm query, valid evidence was found, but appendix and table-derived material ranked above some stronger explanatory passages.

This confirms that good `Hit@K` alone does not imply good evidence ranking.

### Verification

The deterministic test suite currently contains:

**87 passing tests.**

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
* repeatable BM25 evaluation over that benchmark.

---

## In Progress

The lexical retrieval baseline is complete.

The next capability is:

**semantic retrieval evaluation against the fixed benchmark.**

The purpose is not to replace BM25 merely because embeddings are conventional.

The purpose is to test whether semantic retrieval materially improves the measured BM25 weaknesses, particularly:

* paraphrased conceptual queries;
* multi-facet evidence coverage;
* cross-document evidence recovery;
* rank quality.

The fixed `credit-risk-two-paper-v2` benchmark must remain unchanged while semantic retrieval is evaluated.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* semantic embedding generation;
* semantic paragraph retrieval;
* semantic-vs-BM25 benchmark comparison;
* hybrid lexical/semantic retrieval;
* reranking;
* neighbour/context expansion;
* vector persistence;
* retrieval over a larger scholarly corpus;
* normalized-document persistence;
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
* Discovery, verification, relevance assessment, acquisition, normalization, retrieval, and evidence extraction are separate concerns.
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
* Section headings may contribute to retrieval indexing but are not evidence text.
* BM25 is the deterministic lexical baseline.
* Retrieval quality must be measured before architectural escalation.
* Query style and retrieval scope are independent evaluation dimensions.
* Exhaustive relevance recall must not be claimed without exhaustive relevance judgements.
* Current retrieval evaluation uses explicit evidence targets with alternative acceptable anchors.
* The human-reviewed benchmark is pinned to exact artifact hashes.
* The fixed benchmark must be reused when comparing subsequent retrievers.
* A vector database is not required merely to evaluate semantic retrieval.
* Table- and figure-associated paragraphs are not automatically excluded.
* Agent execution must remain bounded.
* Important state is externalised into repository artifacts.
* Human approval remains required for consequential research decisions.
* Every pull request targeting `main` updates `CURRENT_STATE.md`.

### Not Yet Decided

* final thesis topic;
* final thesis research question;
* exact Claude model allocation by agent role;
* embedding provider;
* embedding model;
* semantic similarity implementation;
* hybrid retrieval strategy;
* score-normalization strategy;
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
* final evaluation framework;
* PDF parsing technology;
* whether semantic retrieval materially improves the lexical baseline;
* whether hybrid retrieval is required;
* whether reranking is required;
* whether vector persistence is required;
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

**Evidence:** paraphrased benchmark queries materially underperform lexical queries.

**Mitigation:** evaluate semantic retrieval against the unchanged benchmark.

### RISK-009 — Document parsing fidelity

Machine-readable representations may merge or restructure publication content.

**Mitigation:** immutable raw artifact identity, normalization versioning, and preservation of upstream ambiguity.

### RISK-010 — Evidence-address instability

Normalization changes can invalidate previous paragraph or character addresses.

**Mitigation:** every address includes both artifact identity and normalization version.

### RISK-011 — Retrieval noise

Tables, appendices, or repeated section vocabulary can rank highly despite weaker evidence quality.

**Mitigation:** measure ranking behaviour before introducing filtering or reranking.

### RISK-012 — Benchmark incompleteness

The current benchmark is human-reviewed but not an exhaustive relevance judgement over every query × paragraph pair.

**Mitigation:** evaluate evidence-target satisfaction rather than claiming exhaustive paragraph recall.

### RISK-013 — Small benchmark size

The current retrieval benchmark contains only two documents and twelve queries.

**Mitigation:** use it as a controlled regression and architecture-comparison benchmark, not as evidence of general retrieval quality. Expand evaluation after the retrieval approach is technically established.

### RISK-014 — Benchmark overfitting

Repeatedly changing retrieval logic against a small fixed benchmark could overfit the system to those specific questions.

**Mitigation:** keep the benchmark fixed for the first BM25/semantic comparison, record design changes explicitly, and later add held-out documents and queries.

---

## Known Unknowns

The authoritative list of major unresolved project questions remains in `PROJECT.md`.

Current high-priority unknowns include:

1. University thesis requirements.
2. University policy for AI-assisted academic work.
3. Final FinTech thesis topic.
4. Reliable criteria for topic researchability.
5. Dataset availability for candidate topics.
6. Whether current full-text resolution provides sufficient literature coverage.
7. Which embedding model is appropriate for scholarly evidence retrieval.
8. Whether semantic retrieval improves paraphrase and cross-document evidence coverage.
9. Whether BM25 and semantic retrieval are complementary enough to justify hybrid retrieval.
10. Whether section paths should receive different ranking weight from paragraph text.
11. Whether neighbouring passages should be included after retrieval.
12. Whether a dedicated reranker is necessary.
13. Whether vector persistence is justified once the corpus grows.
14. How tables, figures, equations, and non-prose evidence should eventually be represented.
15. How PDF-only papers should be normalized.
16. How large the retrieval benchmark must become before retrieval architecture is considered stable.
17. Which persistence representation should eventually store source → artifact → document → retrieval → evidence → claim relationships.

---

## Next Actions

1. Preserve `credit-risk-two-paper-v2` unchanged as the initial retrieval comparison benchmark.
2. Define a minimal semantic retriever behind the existing `Retriever` protocol.
3. Select an embedding model based on explicit requirements rather than framework convenience.
4. Generate embeddings for the existing 212 retrieval units.
5. Keep the first semantic index in memory; do not introduce a vector database yet.
6. Run semantic retrieval against exactly the same 12 benchmark cases.
7. Compare:

  * Hit@5;
  * Complete@5;
  * Target Coverage@5;
  * MRR.
8. Inspect per-case changes, especially:

  * `combined_nontraditional_predictors`;
  * `ml_advantage_conditions`;
  * `sample_size_sensitivity_cross_paper`.
9. Determine whether semantic retrieval fixes measured BM25 failures or introduces different ones.
10. Evaluate hybrid retrieval only if the comparison demonstrates complementary failure modes.
11. Introduce reranking only if ranking quality remains a measured problem after candidate generation.
12. Expand the benchmark to additional papers before claiming general retrieval quality.
13. Begin Claude-backed evidence extraction only after retrieval candidate quality is sufficiently stable and measurable.

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
* relevant evidence can be extracted with exact provenance;
* research gaps can be evaluated adversarially;
* datasets, baselines, metrics, and experimental feasibility can be assessed;
* researchability dimensions can be assembled into a structured report;
* unresolved questions remain explicit;
* a human can approve, reject, or request further investigation;
* the complete decision path is auditable from repository artifacts.
