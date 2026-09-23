# Current Project State

Last updated: 2026-09-23

## Current Phase

**Phase 1 — Topic Researchability**

The project is implementing the first executable research workflow for determining whether a proposed thesis topic is sufficiently researchable.

Phase 0 — Project Foundation — is complete.

The first bounded literature discovery, verification, and relevance-assessment workflow is operational.

---

## Current Objective

Extend the Topic Researchability workflow from bibliographic discovery and abstract-level relevance assessment toward evidence-backed research over retrieved scholarly source text.

The current focus is:

**source-text resolution and immutable artifact acquisition with explicit provenance.**

The system can now discover potential full-text locations for scholarly sources, select a preferred machine-readable or PDF representation, retrieve supported artifacts, validate the returned content, and establish immutable artifact identity using SHA-256.

The next capability is deterministic normalization of retrieved scholarly documents into structured text suitable for later evidence extraction.

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
* Sources without sufficient textual evidence terminate deterministically as `INSUFFICIENT_EVIDENCE` rather than forcing an LLM judgment.
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

The result demonstrated that the next material bottleneck was not literature retrieval precision but textual evidence availability.

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
* Current preferred order is:

  1. OpenAlex GROBID XML;
  2. OpenAlex cached PDF;
  3. original open-access PDF.
* Landing pages are not treated as downloadable full text.

A real source-text coverage diagnostic was executed over the nine sources previously terminating without abstract-level evidence.

Results:

* 9 sources lacked abstract-level evidence;
* 2 had OpenAlex GROBID XML;
* 2 had OpenAlex cached PDF;
* 3 had original open-access PDF locations;
* 3 had landing-page locations;
* 5 had no usable text location through the current OpenAlex resolver.

Inspecting all OpenAlex locations rather than only `best_oa_location` did not improve coverage for this sample.

This established that incomplete full-text coverage must remain an explicit supported state rather than triggering unbounded provider searching.

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
* Artifact metadata preserves the source text location used for retrieval.
* Provider credentials are not stored in provenance artifacts.

A live authenticated OpenAlex GROBID download was successfully executed for:

`Corporate default forecasting with machine learning`

OpenAlex work:

`W3010059221`

The live artifact had:

* format: `GROBID_XML`;
* size: `234692` bytes;
* content type: `application/xml; charset=utf-8`;
* SHA-256: `ae21bed28e5f9ab69878493e474bb41537621bebe692018944ed1cc2311d1d67`.

The artifact was confirmed to contain valid TEI XML generated by GROBID, including structured scholarly metadata such as the article title.

### Verification

The current deterministic test suite contains:

**43 passing tests.**

The source-text resolution and artifact-fetching components have additionally been exercised against real OpenAlex data and real OpenAlex full-text infrastructure.

---

## In Progress

The current implementation boundary ends at immutable raw scholarly artifacts.

The next capability is:

**GROBID TEI XML → structured `NormalizedDocument`.**

The system should deterministically transform a retrieved machine-readable scholarly document into a normalized internal representation containing, at minimum:

* document title;
* abstract;
* hierarchical sections;
* paragraphs;
* stable paragraph ordering;
* artifact SHA-256;
* source-provider identity;
* sufficient provenance for later evidence-span attribution.

This normalization must occur before chunking, retrieval, evidence extraction, or additional Claude reasoning.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* `NormalizedDocument` domain representation;
* GROBID TEI normalization;
* PDF document parsing;
* normalized document persistence;
* paragraph-level source offsets or equivalent fine-grained provenance;
* document chunking;
* semantic passage retrieval;
* evidence-span extraction;
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
* orchestration framework selection.

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
* Scholarly discovery, bibliographic verification, relevance assessment, source-text acquisition, document normalization, and evidence extraction are separate concerns.
* Search-planning output is not research evidence.
* The literature search planner must not formulate the final thesis research question.
* The literature search planner must not invent research gaps, findings, datasets, or contributions.
* Planner-driven scholarly discovery uses OpenAlex semantic retrieval.
* OpenAlex lexical retrieval remains available as an explicit alternative.
* DOI metadata verification is provider-independent.
* Crossref coverage must not be treated as equivalent to universal DOI coverage.
* Multiple DOI metadata providers may participate behind a common registry boundary.
* Bibliographic identity verification should remain deterministic where possible.
* Source identity confirmation does not establish source relevance.
* Source relevance does not establish evidential support for a research claim.
* Titles alone are insufficient evidence for relevance classification.
* Missing evidence must remain explicit rather than being converted into artificial certainty.
* Duplicate sources should be removed before expensive downstream verification or LLM reasoning.
* Provider-specific operational constraints belong inside integration boundaries.
* Authentication credentials must not be stored in provenance artifacts.
* A scholarly source and a retrievable representation of that source are different domain concepts.
* One scholarly source may have multiple textual representations.
* Landing pages must not automatically be treated as full-text documents.
* GROBID XML is preferred over PDF when an appropriate machine-readable representation is already available.
* Original downloaded bytes must be identifiable independently using a cryptographic content hash.
* Document parsing should occur deterministically before LLM reasoning over full scholarly text.
* Markdown may later be produced as an LLM-friendly rendering, but it should not be the canonical research-provenance representation.
* Full libraries of papers should not be supplied directly to an LLM context.
* Future reasoning should operate over selected evidence derived from normalized source documents.
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
* final scholarly-document normalization schema;
* chunking strategy;
* evidence-retrieval strategy;
* whether vector retrieval is necessary;
* whether a dedicated workflow engine will be required.

---

## Current Risks

### RISK-001 — Premature architecture

The project may adopt orchestration, persistence, retrieval, or agent frameworks before concrete workflow requirements justify them.

**Mitigation:** continue implementing minimal executable slices before selecting infrastructure.

### RISK-002 — Model-generated false certainty

Claude or another reasoning model may classify or interpret research artifacts more confidently than the available evidence supports.

**Mitigation:** use structured outputs, explicit uncertainty states, bounded responsibilities, deterministic gates, external evidence, and evaluation.

### RISK-003 — Relevance misclassification

A scholarly search provider may return legitimate but topically irrelevant publications, and an LLM relevance classifier may also make incorrect relevance judgments.

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

Machine-readable scholarly representations may lose, alter, or restructure information from the original publication.

PDF extraction may additionally suffer from reading-order, table, equation, figure, column, and layout errors.

**Mitigation:** preserve immutable raw artifact bytes and their SHA-256 identity, maintain provenance from normalized text back to the raw artifact, and validate parsing behaviour against real scholarly documents before downstream evidence extraction relies on it.

### RISK-010 — Provider-authenticated artifact access

Some OpenAlex-hosted cached full-text artifacts require authenticated access even when their location is returned through OpenAlex metadata.

**Mitigation:** keep authentication ephemeral and provider-specific. Do not embed secrets into `SourceTextLocation`, `FetchedArtifact`, or downstream provenance.

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
8. What normalized scholarly-document representation best preserves useful structure and evidence provenance.
9. Whether paragraph-level provenance is sufficient or exact character/span offsets will be required.
10. How PDF-only documents should be parsed once GROBID-first normalization is validated.
11. Whether orchestration requirements will justify introducing a dedicated workflow framework.
12. Which persistence representation should eventually store source → artifact → document → evidence → claim relationships.

---

## Next Actions

1. Introduce the minimal `NormalizedDocument` domain model.
2. Implement deterministic parsing of GROBID TEI XML.
3. Preserve the originating artifact SHA-256 on every normalized document.
4. Preserve section hierarchy and stable paragraph ordering.
5. Validate the parser against synthetic deterministic fixtures.
6. Execute the parser against the real `W3010059221` GROBID artifact.
7. Inspect the resulting real document structure before deciding whether additional provenance fields are necessary.
8. Define the minimum stable evidence-addressing contract.
9. Only then design document chunking and passage retrieval.
10. Introduce Claude-backed evidence extraction only after deterministic normalization and retrieval are sufficiently reliable.

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
* relevant passages can be retrieved without sending an entire literature corpus to an LLM;
* relevant evidence can be extracted with provenance;
* plausible research gaps can be evaluated adversarially;
* data availability and experimental feasibility can be assessed;
* researchability dimensions can be assembled into a structured report;
* unresolved questions remain explicit;
* a human can approve, reject, or request further research on a candidate topic;
* the complete decision path is auditable from repository artifacts.
