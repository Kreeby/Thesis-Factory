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
* human-reviewed retrieval benchmarking;
* lexical-versus-semantic retrieval comparison.

The project has now demonstrated complementary failure modes between lexical and semantic retrieval.

The next retrieval question is whether a bounded deterministic hybrid retriever can combine their strengths without introducing unnecessary architecture.

---

## Current Objective

Determine whether hybrid lexical-semantic retrieval materially improves evidence completeness and ranking quality over either BM25 or semantic retrieval alone.

The hybrid experiment must use the same fixed benchmark:

`credit-risk-two-paper-v2`

The benchmark must not be modified to favour the hybrid implementation.

The next retrieval implementation should remain minimal:

* no vector database;
* no LLM reranker;
* no learned reranker;
* no automatic paragraph splitting;
* no automatic paragraph merging;
* no benchmark-specific heuristics.

The goal is to test whether deterministic fusion of the existing BM25 and semantic candidate lists improves measured research-evidence retrieval.

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
* retrieval units use Voyage `document` input type.
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
* Retrieval evaluation is independent of BM25 and can be reused for semantic and future hybrid retrievers.
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

These aggregate lexical metrics were identical to BM25.

Paraphrased queries:

* `Hit@5`: `0.8571`;
* `Complete@5`: `0.7143`;
* `Target Coverage@5`: `0.7857`;
* MRR: `0.7857`.

Relative to BM25 paraphrase performance:

* `Hit@5`: unchanged;
* `Complete@5`: `+0.1429`;
* `Target Coverage@5`: `+0.0714`;
* MRR: `+0.3214`.

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

Semantic retrieval therefore improved ranking quality substantially while aggregate cross-document evidence completeness remained unchanged.

### Observed Lexical and Semantic Complementarity

The comparison exposed complementary failure modes.

#### Semantic improvement — combined nontraditional predictors

For:

`combined_nontraditional_predictors`

BM25:

* `Hit@5 = false`;
* `Complete@5 = false`;
* target coverage: `0`.

Voyage semantic retrieval:

* `Hit@5 = true`;
* `Complete@5 = true`;
* target coverage: `1.0`;
* first acceptable passage ranked `#1`.

Semantic retrieval therefore recovered a conceptual paraphrase missed entirely by BM25.

#### Semantic improvement — cross-paper sample-size evidence

For:

`sample_size_sensitivity_cross_paper`

BM25:

* recovered only the alternative-data sample-size target;
* target coverage: `0.5`;
* complete: `false`.

Voyage semantic retrieval:

* recovered both the corporate-default and alternative-data targets;
* target coverage: `1.0`;
* complete: `true`;
* first acceptable passage ranked `#1`.

#### Semantic regression — ML advantage conditions

For:

`ml_advantage_conditions`

BM25:

* recovered the `rich-information` target;
* target coverage: `0.5`.

Voyage semantic retrieval:

* recovered no benchmark evidence target in the top five;
* target coverage: `0`.

The semantic top results concentrated on broader statistical-model material rather than the evidence requirements.

#### Semantic regression — information richness across papers

For:

`information_richness_cross_paper`

BM25:

* recovered both document-specific evidence targets;
* target coverage: `1.0`;
* complete: `true`.

Voyage semantic retrieval:

* recovered only the corporate-default evidence target;
* target coverage: `0.5`;
* complete: `false`.

The semantic ranking concentrated too strongly on one source and failed to preserve cross-document evidence diversity.

### Retrieval Decision

Semantic retrieval is valuable but should not replace BM25.

The benchmark demonstrates:

* BM25 remains strong on direct lexical matches;
* semantic retrieval materially improves paraphrase ranking and some evidence-completeness failures;
* semantic retrieval can lose evidence that BM25 retrieves;
* semantic ranking may concentrate top results around one semantic cluster or source;
* the two retrievers exhibit complementary failure modes.

This provides empirical justification for evaluating hybrid retrieval.

It does not yet prove that a hybrid retriever will outperform both systems.

### Verification

The deterministic test suite currently contains:

**102 passing tests.**

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
* lexical-versus-semantic benchmark comparison.

---

## In Progress

The semantic retrieval baseline is complete.

The next capability is:

**hybrid lexical-semantic retrieval evaluation.**

The purpose is to determine whether combining candidate rankings from BM25 and semantic retrieval can improve:

* evidence completeness;
* target coverage;
* ranking quality;
* resilience to complementary lexical and semantic failure modes.

The hybrid design must remain deterministic and minimal.

The fixed `credit-risk-two-paper-v2` benchmark must remain unchanged during the first hybrid comparison.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* hybrid lexical-semantic retrieval;
* hybrid retrieval benchmark comparison;
* reranking;
* source-diversity-aware retrieval;
* neighbour/context expansion;
* vector persistence;
* retrieval over a larger scholarly corpus;
* held-out retrieval benchmark;
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
* Section paths may contribute to retrieval representations but are not evidence text.
* BM25 is the deterministic lexical baseline.
* Semantic retrieval operates through a provider-independent embedding boundary.
* `voyage-4` is the current measured semantic baseline model.
* Cosine similarity is the current semantic ranking function.
* The current semantic index remains in memory.
* A vector database is not justified for the current corpus.
* Semantic retrieval materially improves some measured retrieval behaviours.
* Semantic retrieval does not dominate BM25 on every benchmark case.
* Semantic retrieval must not replace BM25 based on the current evidence.
* BM25 and semantic retrieval exhibit complementary measured failure modes.
* Hybrid retrieval is justified for evaluation.
* Retrieval quality must be measured before architectural escalation.
* Query style and retrieval scope are independent evaluation dimensions.
* Exhaustive relevance recall must not be claimed without exhaustive relevance judgements.
* Current retrieval evaluation uses explicit evidence targets with alternative acceptable anchors.
* The human-reviewed benchmark is pinned to exact artifact hashes.
* The fixed benchmark must be reused when comparing subsequent retrievers.
* Table- and figure-associated paragraphs are not automatically excluded.
* Provider calls must be bounded.
* Retry behaviour must be bounded.
* Rate-limit handling belongs inside the provider integration boundary.
* Agent execution must remain bounded.
* Important state is externalised into repository artifacts.
* Human approval remains required for consequential research decisions.
* Every pull request targeting `main` updates `CURRENT_STATE.md`.

### Not Yet Decided

* final thesis topic;
* final thesis research question;
* exact Claude model allocation by agent role;
* final embedding provider;
* final embedding model;
* hybrid retrieval strategy;
* candidate-list depth used before hybrid fusion;
* rank-fusion parameters;
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
* final evaluation framework;
* PDF parsing technology;
* whether hybrid retrieval materially improves both standalone retrievers;
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

**Evidence:** paraphrased benchmark queries materially underperform lexical queries, and BM25 completely missed `combined_nontraditional_predictors`.

**Mitigation:** preserve semantic retrieval as a complementary retrieval signal.

### RISK-009 — Document parsing fidelity

Machine-readable representations may merge or restructure publication content.

**Mitigation:** immutable raw artifact identity, normalization versioning, and preservation of upstream ambiguity.

### RISK-010 — Evidence-address instability

Normalization changes can invalidate previous paragraph or character addresses.

**Mitigation:** every address includes both artifact identity and normalization version.

### RISK-011 — Retrieval noise

Tables, appendices, repeated section vocabulary, or broad semantic similarity may rank highly despite weaker evidence quality.

**Mitigation:** continue measuring ranking behaviour before introducing filtering or reranking.

### RISK-012 — Benchmark incompleteness

The current benchmark is human-reviewed but not an exhaustive relevance judgement over every query × paragraph pair.

**Mitigation:** evaluate evidence-target satisfaction rather than claiming exhaustive paragraph recall.

### RISK-013 — Small benchmark size

The current retrieval benchmark contains only two documents and twelve queries.

**Mitigation:** use it as a controlled regression and architecture-comparison benchmark, not as evidence of general retrieval quality. Add held-out documents and queries after retrieval architecture is technically established.

### RISK-014 — Benchmark overfitting

Repeatedly tuning retrieval logic against the same small fixed benchmark can overfit implementation choices to the benchmark.

**Mitigation:** keep the benchmark fixed for initial architecture comparisons, avoid case-specific heuristics, and create a held-out benchmark before considering retrieval stable.

### RISK-015 — Semantic concentration

Semantic retrieval may return several conceptually similar passages from one source while failing to satisfy distinct evidence targets across documents.

**Evidence:** `information_richness_cross_paper` lost the alternative-data target despite high semantic ranking confidence.

**Mitigation:** evaluate hybrid retrieval first; consider explicit source-diversity mechanisms only if a measured problem remains.

### RISK-016 — External embedding-provider limits

Semantic retrieval depends on an external embedding API whose rate limits, quotas, availability, or pricing may change.

**Mitigation:** keep embedding access behind `TextEmbedder`, use bounded batching/retry/pacing, and preserve the ability to substitute another provider or local implementation.

### RISK-017 — Hybrid complexity without benefit

Hybrid retrieval could add architecture while providing no meaningful benchmark improvement.

**Mitigation:** implement only a minimal deterministic fusion experiment and retain it only if measured results justify it.

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
7. Which embedding provider and model should eventually be used beyond the current baseline.
8. Whether deterministic hybrid retrieval improves on both BM25 and Voyage.
9. Which fusion method should be used if hybrid retrieval is retained.
10. Whether candidate depth greater than final `K` is required for effective fusion.
11. Whether explicit source diversity is required for multi-document research questions.
12. Whether section paths should receive different retrieval weight from paragraph text.
13. Whether neighbouring passages should be included after retrieval.
14. Whether a dedicated reranker is necessary.
15. Whether vector persistence becomes justified as the corpus grows.
16. How tables, figures, equations, and non-prose evidence should eventually be represented.
17. How PDF-only papers should be normalized.
18. How large the retrieval benchmark must become before retrieval architecture is considered stable.
19. Which persistence representation should eventually store source → artifact → document → retrieval → evidence → claim relationships.

---

## Next Actions

1. Merge the completed semantic-retrieval slice without adding hybrid logic to the same branch.
2. Preserve `credit-risk-two-paper-v2` unchanged.
3. Start a separate hybrid-retrieval branch.
4. Define a minimal deterministic fusion retriever over the existing BM25 and semantic retrievers.
5. Avoid raw-score addition because BM25 and cosine scores are not directly comparable.
6. Evaluate rank-based fusion as the first candidate approach.
7. Keep candidate retrieval and final `K` explicitly bounded.
8. Run BM25, semantic, and hybrid retrieval against exactly the same benchmark.
9. Compare:

* `Hit@5`;
* `Complete@5`;
* `Target Coverage@5`;
* MRR.

10. Inspect the known complementary cases:

* `combined_nontraditional_predictors`;
* `ml_advantage_conditions`;
* `information_richness_cross_paper`;
* `sample_size_sensitivity_cross_paper`.

11. Retain hybrid retrieval only if it improves measured behaviour without unacceptable regressions.
12. Evaluate source-diversity constraints only if cross-document target loss remains after fusion.
13. Introduce reranking only if candidate generation remains adequate while top-rank quality is still a measured problem.
14. Add a held-out retrieval evaluation set before treating retrieval architecture as stable.
15. Begin Claude-backed evidence extraction only after retrieval candidate quality is sufficiently stable.

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
* the selected retrieval strategy is justified by measured evidence rather than convention;
* relevant evidence can be extracted with exact provenance;
* research gaps can be evaluated adversarially;
* datasets, baselines, metrics, and experimental feasibility can be assessed;
* researchability dimensions can be assembled into a structured report;
* unresolved questions remain explicit;
* a human can approve, reject, or request further investigation;
* the complete decision path is auditable from repository artifacts.
