# Current Project State

Last updated: 2026-09-23

## Current Phase

**Phase 1 — Topic Researchability**

The project is implementing the first executable research workflow for determining whether a proposed thesis topic is sufficiently researchable.

Phase 0 — Project Foundation — is complete.

---

## Current Objective

Build and validate the minimum Topic Researchability workflow required to transform a candidate research topic into progressively more verified research artifacts.

The first bounded topic-level literature discovery and relevance-assessment loop is now operational.

The current focus is extending that loop from abstract-level relevance assessment toward source-text resolution and evidence extraction with explicit provenance.

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

### Phase 1 — Topic Researchability

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
* Provider-independent structured LLM reasoning boundary implemented.
* Anthropic / Claude structured reasoning adapter implemented.
* Claude-backed scholarly source relevance assessment implemented.
* Relevance assessment uses explicit `RELEVANT`, `NOT_RELEVANT`, `UNCERTAIN`, and `INSUFFICIENT_EVIDENCE` outcomes.
* Sources without sufficient textual evidence terminate deterministically as `INSUFFICIENT_EVIDENCE` without requiring an LLM call.
* Relevance behaviour is covered by deterministic unit tests.
* A curated relevance evaluation harness using real Claude calls has been implemented.
* Bounded `LiteratureSearchPlanner` implemented.
* Search planning is explicitly separated from final thesis research-question formulation.
* Search plans are limited to at most five complementary scholarly search tasks.
* Search-planning output is operational and is not treated as research evidence.
* Topic-level literature assessment workflow implemented.
* Results from multiple planned searches are aggregated before downstream processing.
* Duplicate scholarly sources are removed before bibliographic verification and relevance assessment.
* Search-query provenance is preserved for each discovered source.
* OpenAlex lexical and semantic search modes implemented explicitly.
* Live comparison demonstrated materially better topic precision from OpenAlex semantic retrieval than lexical retrieval for the current candidate topic.
* Planner-driven literature discovery currently uses OpenAlex semantic search.
* OpenAlex semantic-search rate limiting is handled inside the provider integration boundary.
* Crossref abstracts are ingested when available and can act as fallback evidence when OpenAlex lacks an abstract.
* The exact `SourceRecord` used for relevance assessment is preserved as `relevance_source`.
* DataCite fallback was verified against an arXiv DOI not resolved through Crossref.
* The complete bounded literature workflow has been executed against real providers and Claude.
* A real five-query, five-result-per-query run for `machine learning credit risk` produced:

    * 25 unique sources;
    * 14 `RELEVANT`;
    * 0 `NOT_RELEVANT`;
    * 0 `UNCERTAIN`;
    * 9 `INSUFFICIENT_EVIDENCE`;
    * 2 sources not assessed because bibliographic verification could not proceed.
* Current and target Topic Researchability architecture is documented under `docs/architecture/topic-researchability.md`.
* Deterministic workflow behaviour is covered by automated tests.

---

## In Progress

The first bounded literature-discovery and relevance-assessment loop is operational.

The active bottleneck is:

**Source-text resolution for scholarly sources whose available discovery or registry metadata does not contain enough text for evidence-based assessment.**

A significant portion of semantically relevant literature currently terminates as `INSUFFICIENT_EVIDENCE` because neither OpenAlex nor the DOI metadata source provides an abstract.

The next capability should locate legally accessible source text while preserving:

* scholarly-source identity;
* source location;
* provider provenance;
* downloaded-artifact identity;
* exact text used by downstream reasoning.

Sources without sufficient evidence must continue to terminate explicitly rather than being classified from title alone.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* structured source-text location artifacts;
* open-access full-text resolution;
* downloaded-artifact hashing and provenance;
* scholarly document parsing;
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
* persistence of research artifacts;
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
* Scholarly discovery, bibliographic verification, relevance assessment, and evidence extraction are separate concerns.
* Search-planning output is not research evidence.
* The literature search planner must not formulate the final thesis research question.
* The literature search planner must not invent research gaps, findings, datasets, or contributions.
* Planner-driven scholarly discovery uses OpenAlex semantic retrieval.
* OpenAlex lexical retrieval remains available as an explicit alternative rather than being silently replaced.
* DOI metadata verification is provider-independent.
* Crossref coverage must not be treated as equivalent to universal DOI coverage.
* Multiple DOI metadata providers may participate behind a common registry boundary.
* Bibliographic identity verification should remain deterministic where possible.
* Source identity confirmation does not establish source relevance.
* Source relevance does not establish evidential support for a research claim.
* Titles alone are insufficient evidence for relevance classification.
* Missing evidence should remain explicit rather than being converted into artificial certainty.
* Exact evidence provenance must survive downstream transformations.
* Duplicate sources should be removed before expensive downstream verification or LLM reasoning.
* Provider-specific operational constraints such as API throttling belong inside integration boundaries.
* Agent execution must be bounded.
* Important project state must be externalised into repository artifacts.
* Human approval is required for consequential research decisions.
* Technology should be selected in response to executable requirements rather than anticipated future complexity.
* `CURRENT_STATE.md` must be updated as part of every pull request targeting `main`.
* A repository CI gate should prevent a pull request from being merged when `CURRENT_STATE.md` has not been updated.

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
* final scholarly full-text parsing stack;
* whether a dedicated workflow engine will be required.

---

## Current Risks

### RISK-001 — Premature architecture

The project may adopt orchestration, persistence, retrieval, or agent frameworks before concrete workflow requirements justify them.

**Mitigation:** continue implementing minimal executable slices before selecting infrastructure.

### RISK-002 — Model-generated false certainty

Claude or another reasoning model may classify or interpret research artifacts more confidently than the available evidence supports.

**Mitigation:** use structured outputs, explicit uncertainty states, bounded responsibilities, external evidence, deterministic gates, and evaluation.

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

### RISK-007 — Abstract and metadata coverage

Semantically relevant scholarly sources may lack an abstract in OpenAlex or DOI-registry metadata.

This currently prevents evidence-based relevance assessment for a material portion of discovered literature.

**Mitigation:** resolve legally accessible source text with explicit source-location and artifact provenance rather than inferring relevance from titles.

### RISK-008 — Retrieval quality

Keyword-oriented scholarly retrieval may rank broadly related methodological papers above papers directly relevant to the candidate research topic.

**Mitigation:** semantic retrieval is currently used for planner-generated literature searches. Retrieval behaviour should continue to be evaluated empirically rather than assumed from provider ranking.

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
7. Which legally accessible full-text locations provide sufficient coverage for the literature workflow.
8. Whether orchestration requirements will justify introducing a dedicated workflow framework.
9. Which provenance representation should eventually persist source → artifact → evidence → claim relationships.

---

## Next Actions

1. Define the minimal structured artifact representing a scholarly source-text location.
2. Extend the OpenAlex integration to expose open-access text locations without coupling workflow logic to repository-specific providers.
3. Resolve legally accessible source text for papers currently terminating as `INSUFFICIENT_EVIDENCE`.
4. Preserve downloaded-artifact identity and provenance, including a deterministic content hash.
5. Parse resolved scholarly artifacts into text suitable for downstream evidence extraction.
6. Re-run relevance assessment using stronger textual evidence where available.
7. Implement structured evidence-span extraction only after source-text resolution is stable.
8. Use observed failures to determine the next minimal research capability rather than introducing speculative infrastructure.

---

## Current Milestone Exit Criteria

The initial Topic Researchability milestone is complete when:

* a candidate topic can drive bounded scholarly literature planning;
* planned searches can drive scholarly literature discovery;
* duplicate discoveries can be consolidated without losing query provenance;
* discovered sources can be bibliographically verified across appropriate metadata registries;
* source relevance can be assessed with explicit uncertainty;
* insufficient evidence rem*
