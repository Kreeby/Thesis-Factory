# Current Project State

Last updated: 2026-09-23

## Current Phase

**Phase 1 — Topic Researchability**

The project is implementing the first executable research workflow for determining whether a proposed thesis topic is sufficiently researchable.

Phase 0 — Project Foundation — is complete.

---

## Current Objective

Build and validate the minimum Topic Researchability workflow required to transform a candidate research topic into progressively more verified research artifacts.

The current focus is adding the first bounded LLM reasoning component on top of the deterministic scholarly discovery and bibliographic verification pipeline.

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
* Crossref DOI lookup integration implemented.
* Bibliographic metadata comparison implemented.
* Source identity verification implemented with explicit `CONFIRMED`, `CONFLICTING`, and `INSUFFICIENT_DATA` outcomes.
* Verification discrepancies are preserved rather than hidden.
* `discover_and_verify_sources` workflow implemented.
* The workflow has been executed against real OpenAlex and Crossref data.
* Current and target Topic Researchability architecture documented under `docs/architecture/topic-researchability.md`.
* Deterministic workflow behaviour is covered by automated tests.

---

## In Progress

Implementation of the first Claude-backed reasoning component:

**Scholarly source relevance assessment.**

The intended input is:

* candidate research topic;
* bibliographically verified scholarly source;
* title;
* available abstract.

The intended output is a structured relevance artifact rather than unrestricted prose.

Sources without sufficient textual evidence should terminate as insufficient evidence without requiring an LLM call.

---

## Not Started

The following Phase 1 capabilities have not yet been implemented:

* Claude-backed relevance assessment;
* relevance evaluation against a curated test set;
* research-query planning;
* evidence extraction;
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
* final research question;
* experiment implementation;
* thesis writing;
* final academic audit.

---

## Active Decisions

### Confirmed

* Claude models accessed through the Anthropic API are the default LLM family for autonomous reasoning agents.
* Model-provider concerns should remain isolated behind project-controlled boundaries where practical.
* LLM output is not factual evidence.
* Scholarly discovery and bibliographic verification are separate concerns.
* Bibliographic identity verification should remain deterministic where possible.
* Source identity confirmation does not establish source relevance.
* Source relevance does not establish evidential support for a research claim.
* Missing evidence should remain explicit rather than being converted into artificial certainty.
* Agent execution must be bounded.
* Important project state must be externalised into repository artifacts.
* Human approval is required for consequential research decisions.
* Technology should be selected in response to executable requirements rather than anticipated future complexity.

### Not Yet Decided

* final thesis topic;
* final research question;
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
* final evaluation framework.

---

## Current Risks

### RISK-001 — Premature architecture

The project may adopt orchestration, persistence, retrieval, or agent frameworks before concrete workflow requirements justify them.

**Mitigation:** continue implementing minimal executable slices before selecting infrastructure.

### RISK-002 — Model-generated false certainty

Claude or another reasoning model may classify or interpret research artifacts more confidently than the available evidence supports.

**Mitigation:** use structured outputs, explicit uncertainty states, bounded responsibilities, external evidence, and evaluation.

### RISK-003 — Relevance misclassification

A scholarly search provider may return legitimate but topically irrelevant publications, and an LLM relevance classifier may also make incorrect relevance judgments.

**Mitigation:** keep discovery separate from relevance assessment and introduce explicit evaluation cases before relying on relevance decisions downstream.

### RISK-004 — Incomplete scholarly metadata

Different scholarly providers may expose different author names, publication dates, venue representations, or missing abstracts.

**Mitigation:** preserve provider-specific discrepancies and avoid requiring exact agreement on secondary metadata to establish identity.

### RISK-005 — Unbounded agent cost

Future autonomous research or review loops may consume excessive model calls and tokens without meaningful progress.

**Mitigation:** introduce explicit execution budgets before multi-step autonomous agent loops are enabled.

### RISK-006 — Documentation drift

Canonical documentation may fall behind the actual repository state.

**Mitigation:** update `CURRENT_STATE.md` at meaningful workflow boundaries and treat executable code and tests as authoritative for runtime behaviour.

---

## Known Unknowns

The authoritative list of major unresolved project questions is maintained in `PROJECT.md`.

Current high-priority unknowns are:

1. University thesis requirements.
2. University policy for AI-assisted academic work.
3. Final FinTech thesis topic.
4. Reliable criteria for determining topic researchability.
5. Data availability for candidate research topics.
6. How relevance assessments should be evaluated before being trusted downstream.
7. Whether orchestration requirements will justify introducing a dedicated workflow framework.

---

## Next Actions

1. Implement the provider-independent structured reasoning boundary.
2. Implement the Anthropic / Claude structured reasoning adapter.
3. Implement scholarly source relevance assessment.
4. Test relevance behaviour without external API calls using deterministic fakes.
5. Execute relevance assessment against real discovered and verified scholarly sources.
6. Use observed failures to define the next minimal Topic Researchability capability.

---

## Current Milestone Exit Criteria

The initial Topic Researchability milestone is complete when:

* a candidate topic can drive scholarly literature discovery;
* discovered sources can be bibliographically verified;
* source relevance can be assessed with explicit uncertainty;
* relevant evidence can be extracted with provenance;
* plausible research gaps can be evaluated adversarially;
* data availability and experimental feasibility can be assessed;
* researchability dimensions can be assembled into a structured report;
* unresolved questions remain explicit;
* a human can approve, reject, or request further research on a candidate topic;
* the complete decision path is auditable from repository artifacts.
