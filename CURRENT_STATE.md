# Current Project State

Last updated: 2026-09-23

## Current Phase

**Phase 1 — Topic Researchability**

Phase 0 — Project Foundation — is complete.

The first bounded literature discovery, verification, relevance-assessment, source-text resolution, artifact-acquisition, and document-normalization capabilities are operational.

The project is now moving from normalized scholarly documents toward exact evidence addressing and retrieval.

---

## Current Objective

Extend the Topic Researchability workflow from normalized scholarly source text toward evidence that can be retrieved, inspected, cited, and independently verified.

The current focus is:

**stable evidence addressing over normalized scholarly documents.**

A retrieved scholarly artifact can now be transformed deterministically into a structured `NormalizedDocument` while preserving its immutable artifact identity.

The next capability must make it possible to identify an exact span of normalized source text using a stable structured address and to verify mechanically that the referenced text actually exists at that address.

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
* A GitHub Actions Current State Gate has been added to enforce the `CURRENT_STATE.md` update invariant.

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
* Source identity verification implemented with explicit `CONFIRMED`, `CONFLICTING`, and `INSUFFICIENT_DATA` outcomes.
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

The result demonstrated that the next material bottleneck was textual evidence availability rather than initial retrieval precision.

### Phase 1 — Source-Text Resolution

* `SourceTextLocation` introduced as a domain artifact distinct from bibliographic `SourceRecord`.
* Bibliographic source identity and retrievable textual representations are modelled separately.
* OpenAlex full-text location lookup implemented.
* OpenAlex `best_oa_location` support implemented.
* OpenAlex complete `locations` inspection implemented.
* OpenAlex cached full-text `content_urls` support implemented.
* Supported text-location representations include:

  * OpenAlex GROBID XML;
  * OpenAlex cached PDF;
  * original open-access PDF;
  * scholarly landing page.
* Multiple text locations for the same source are deduplicated.
* Landing pages are distinguished from directly downloadable full-text artifacts.
* Preferred text location selection implemented.
* Preferred order is:

  1. OpenAlex GROBID XML;
  2. OpenAlex cached PDF;
  3. original open-access PDF.
* Landing pages are not treated as downloadable full text.

A real source-text coverage diagnostic over the nine sources previously terminating without abstract-level evidence found:

* 9 sources lacking abstract-level evidence;
* 2 with OpenAlex GROBID XML;
* 2 with OpenAlex cached PDF;
* 3 with original open-access PDF locations;
* 3 with landing-page locations;
* 5 with no usable text location through the current OpenAlex resolver.

Inspecting all OpenAlex locations rather than only `best_oa_location` did not improve coverage for this sample.

Incomplete full-text coverage is therefore treated as an explicit supported state rather than as a trigger for unbounded provider searching.

### Phase 1 — Artifact Acquisition

* Deterministic artifact-fetching capability implemented.
* Direct full-text locations can be downloaded independently of reasoning agents.
* Supported downloaded artifact formats currently include:

  * GROBID XML;
  * PDF.
* Downloaded artifacts are validated against their expected representation.
* HTML or access-denied responses masquerading as PDF are rejected.
* Empty artifacts are rejected.
* Maximum artifact size is bounded.
* Downloaded artifact bytes are assigned a deterministic SHA-256 identity.
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

* `NormalizedDocument` domain representation implemented.
* `NormalizedSection` domain representation implemented.
* `NormalizedParagraph` domain representation implemented.
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
* Both standard GROBID TEI structure and the older OpenAlex GROBID representation are supported.
* TEI namespaces are handled without hard-coding a single namespace layout.
* Main article title extraction implemented.
* Abstract extraction implemented.
* Body-section extraction implemented.
* Nested section paths are preserved where the upstream document represents them structurally.
* Stable global paragraph ordinals are assigned during normalization.
* Original `xml:id` values are preserved when available.
* Inline TEI elements such as references are flattened into readable normalized paragraph text.
* Whitespace is deterministically normalized.
* Empty or unusable documents are rejected.
* Non-GROBID artifacts are rejected by the GROBID parser.
* Section heading roles are represented separately from section content type.
* Current heading roles are:

  * `STANDARD`;
  * `TABLE`;
  * `FIGURE`.
* Table-like and figure-like headings are identified without treating the entire corresponding section as exclusively table or figure content.
* This distinction preserves ordinary prose that GROBID may place inside a `<div>` whose heading begins with `Table` or `Figure`.
* Upstream structural ambiguities are preserved rather than silently repaired with invented hierarchy.

A real normalization run was completed for the authenticated GROBID artifact of:

`Corporate default forecasting with machine learning`

The resulting normalized document contained:

* title: `CORPORATE DEFAULT FORECASTING WITH MACHINE LEARNING`;
* normalization version: `grobid-tei-v1`;
* artifact SHA-256: `ae21bed28e5f9ab69878493e474bb41537621bebe692018944ed1cc2311d1d67`;
* 25 normalized sections;
* 119 normalized paragraphs.

The real document successfully exposed meaningful scholarly structure including:

* abstract;
* introduction;
* related literature;
* statistical-model discussion;
* machine-learning-model discussion;
* training data;
* model calibration;
* results;
* discriminatory-power evaluation;
* backtesting;
* credit allocation;
* variable importance;
* conclusions;
* appendices.

The real run also demonstrated upstream GROBID imperfections such as merged headings including:

`THE TRAINING DATASET 4.1 CORPORATE DEFAULTS`

and:

`APPENDICES APPENDIX 1`.

These are currently preserved exactly rather than being separated using unsupported heuristics.

### Verification

After the final normalization changes, the deterministic test suite is expected to contain:

**50 passing tests.**

The normalization pipeline has additionally been exercised against a real 234 KB OpenAlex GROBID artifact.

---

## In Progress

The current implementation boundary ends at deterministic normalized scholarly documents.

The next capability is:

**stable evidence addressing.**

The system must be able to identify an exact span of normalized scholarly text in a form that is:

* deterministic;
* serializable;
* independently verifiable;
* tied to the immutable raw artifact;
* tied to the normalization algorithm version;
* precise enough for downstream evidence extraction and claim verification.

The initial target addressing chain is:

`artifact SHA-256 → normalization version → paragraph ordinal → character span`

Section identity may additionally be preserved for navigation and consistency checking.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* stable text-span addressing;
* deterministic evidence-span validation;
* normalized document persistence;
* document chunking;
* semantic passage retrieval;
* evidence extraction;
* structured evidence artifacts;
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
* Model-provider concerns should remain isolated behind project-controlled boundaries where practical.
* LLM output is not factual evidence.
* Scholarly discovery, bibliographic verification, relevance assessment, source-text acquisition, normalization, retrieval, and evidence extraction are separate concerns.
* Search-planning output is not research evidence.
* The literature search planner must not formulate the final thesis research question.
* The literature search planner must not invent research gaps, findings, datasets, or contributions.
* Planner-driven scholarly discovery uses OpenAlex semantic retrieval.
* OpenAlex lexical retrieval remains available as an explicit alternative.
* DOI metadata verification is provider-independent.
* Crossref coverage must not be treated as equivalent to universal DOI coverage.
* Bibliographic identity verification should remain deterministic where possible.
* Source identity confirmation does not establish source relevance.
* Source relevance does not establish evidential support for a research claim.
* Titles alone are insufficient evidence for relevance classification.
* Missing evidence must remain explicit rather than being converted into artificial certainty.
* Duplicate sources should be removed before expensive downstream processing.
* Provider-specific operational constraints belong inside integration boundaries.
* Authentication credentials must not be stored in provenance artifacts.
* A scholarly source and a retrievable representation of that source are different domain concepts.
* One scholarly source may have multiple textual representations.
* Landing pages must not automatically be treated as full-text documents.
* GROBID XML is preferred over PDF when an appropriate machine-readable representation is already available.
* Raw downloaded artifacts are identified using SHA-256.
* Document normalization occurs deterministically before LLM reasoning over full scholarly text.
* Normalization algorithms are explicitly versioned.
* Normalized paragraph order must be deterministic.
* Upstream structural uncertainty must not be silently repaired by invented document structure.
* Table- or figure-like headings do not prove that every paragraph within the corresponding upstream GROBID `<div>` belongs exclusively to a table or figure.
* Markdown may later be produced as an LLM-friendly rendering, but it is not the canonical provenance representation.
* Full libraries of papers should not be supplied directly to an LLM context.
* Future reasoning should operate over selected evidence derived from normalized documents.
* Inability to retrieve full text is a valid explicit outcome.
* Full-text resolution must not become an unbounded provider-search loop.
* Agent execution must be bounded.
* Important project state must be externalised into repository artifacts.
* Human approval is required for consequential research decisions.
* Technology should be selected in response to executable requirements rather than anticipated future complexity.
* Every pull request targeting `main` must update `CURRENT_STATE.md`.
* The repository Current State Gate should prevent merging when that invariant is violated.

### Not Yet Decided

* final thesis topic;
* final thesis research question;
* exact Claude model allocation by agent role;
* orchestration framework;
* persistence technology;
* vector or retrieval technology;
* execution sandbox;
* experiment tracking system;
* observability stack;
* deployment architecture;
* final agent topology;
* final provenance persistence schema;
* final evaluation framework;
* PDF parsing technology;
* chunking strategy;
* evidence-retrieval strategy;
* whether vector retrieval is necessary;
* whether a dedicated workflow engine will be required;
* whether future normalization versions should represent tables and figures as independent first-class document nodes.

---

## Current Risks

### RISK-001 — Premature architecture

The project may adopt orchestration, persistence, retrieval, or agent frameworks before concrete workflow requirements justify them.

**Mitigation:** continue implementing minimal executable slices before selecting infrastructure.

### RISK-002 — Model-generated false certainty

Claude or another reasoning model may classify or interpret research artifacts more confidently than the available evidence supports.

**Mitigation:** use structured outputs, explicit uncertainty states, deterministic gates, external evidence, and evaluation.

### RISK-003 — Relevance misclassification

A scholarly search provider may return legitimate but topically irrelevant publications, and an LLM relevance classifier may make incorrect relevance judgments.

**Mitigation:** keep discovery separate from relevance assessment, maintain explicit evaluation cases, and preserve uncertainty rather than forcing classification.

### RISK-004 — Incomplete scholarly metadata

Different scholarly providers may expose different author names, publication dates, venue representations, DOI coverage, or missing abstracts.

**Mitigation:** preserve provider-specific discrepancies, support multiple metadata registries, and avoid requiring exact agreement on secondary metadata to establish identity.

### RISK-005 — Unbounded agent cost

Future autonomous research or review loops may consume excessive model calls and tokens without meaningful progress.

**Mitigation:** use explicit limits for search fan-out and introduce additional execution budgets before broader autonomous loops are enabled.

### RISK-006 — Documentation drift

Canonical documentation may fall behind the actual repository state.

**Mitigation:** every pull request targeting `main` must update `CURRENT_STATE.md`. A required CI status check should prevent merge when that update is absent. Executable code and tests remain authoritative for runtime behaviour.

### RISK-007 — Incomplete full-text availability

A material subset of relevant scholarly sources may not expose usable open full text through the currently supported resolver.

In the current diagnostic sample, five of nine sources without abstract-level evidence had no usable full-text location through OpenAlex.

**Mitigation:** treat text unavailability as an explicit state. Do not infer paper content from titles and do not introduce unbounded repository/provider searching.

### RISK-008 — Retrieval quality

Keyword-oriented scholarly retrieval may rank broadly related methodological papers above papers directly relevant to the candidate research topic.

**Mitigation:** semantic retrieval is currently used for planner-generated literature searches. Retrieval behaviour should continue to be evaluated empirically.

### RISK-009 — Document parsing fidelity

Machine-readable scholarly representations may lose, alter, merge, or restructure information from the original publication.

The real GROBID normalization run demonstrated merged headings and ambiguous table/figure containers.

**Mitigation:** preserve immutable raw artifact bytes and their SHA-256 identity, version the normalization algorithm, preserve upstream ambiguity, avoid unsupported reconstruction, and validate parsing against real scholarly documents.

### RISK-010 — Provider-authenticated artifact access

Some OpenAlex-hosted cached full-text artifacts require authenticated access even when their location is returned through OpenAlex metadata.

**Mitigation:** keep authentication ephemeral and provider-specific. Do not embed secrets into `SourceTextLocation`, `FetchedArtifact`, or downstream provenance.

### RISK-011 — Evidence-address instability

Offsets or paragraph identities may change when normalization logic changes, potentially invalidating previously extracted evidence.

**Mitigation:** every evidence address must include the source artifact identity and normalization version. Evidence validation must fail explicitly when the referenced normalized document does not match that identity.

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
8. Whether normalized paragraph-level text is sufficient for the majority of evidence extraction.
9. What exact evidence-address schema should be stable across the research pipeline.
10. How evidence derived from tables, figures, equations, or other non-prose structures should eventually be represented.
11. How PDF-only documents should be normalized once GROBID-first processing is sufficiently mature.
12. Whether orchestration requirements will justify introducing a dedicated workflow framework.
13. Which persistence representation should eventually store source → artifact → document → evidence → claim relationships.

---

## Next Actions

1. Define the minimal stable text-span address.
2. Include artifact SHA-256 and normalization version in every address.
3. Address normalized paragraphs by deterministic paragraph ordinal.
4. Add zero-based character start/end offsets within the normalized paragraph.
5. Implement deterministic resolution of an address against a `NormalizedDocument`.
6. Reject addresses targeting the wrong artifact or normalization version.
7. Reject invalid paragraph ordinals and character ranges.
8. Preserve the exact resolved text as evidence.
9. Validate the addressing model against the real normalized `W3010059221` document.
10. Only after stable evidence addressing exists, design chunking and passage retrieval.
11. Introduce Claude-backed evidence extraction only after deterministic retrieval can return verifiable source spans.

---

## Current Milestone Exit Criteria

The initial Topic Researchability milestone is complete when:

* a candidate topic can drive bounded scholarly literature planning;
* planned searches can drive scholarly literature discovery;
* duplicate discoveries can be consolidated without losing query provenance;
* discovered sources can be bibliographically verified across appropriate metadata registries;
* source relevance can be assessed with explicit uncertainty;
* insufficient evidence remains explicit;
* usable scholarly full text can be resolved where available;
* retrieved artifacts have immutable identity and preserved provenance;
* scholarly artifacts can be deterministically normalized into structured documents;
* exact evidence spans can be addressed and verified deterministically;
* relevant passages can be retrieved without sending an entire literature corpus to an LLM;
* relevant evidence can be extracted with provenance;
* plausible research gaps can be evaluated adversarially;
* data availability and experimental feasibility can be assessed;
* researchability dimensions can be assembled into a structured report;
* unresolved questions remain explicit;
* a human can approve, reject, or request further research on a candidate topic;
* the complete decision path is auditable from repository artifacts.
