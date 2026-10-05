# Current Project State

Last updated: 2026-10-05

## Current Phase

**Phase 1 — Evidence Acquisition and Proposal Research**

Phase 0 — Project Foundation — is complete.

The approved thesis topic is:

`A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring`

The retrieval architecture comparison cycle is complete for the current Phase 1 scope. Voyage `voyage-4` remains the selected default semantic retriever for evidence acquisition, with BM25 retained as the deterministic lexical baseline and diagnostic comparator.

The system now supports bounded proposal-oriented research from an approved topic through discovery, verification, exact evidence extraction, research synthesis, adversarial critique, and proposal writing.

The immediate objective is to finish the Project Proposal from the evidence already collected, without opening another broad research loop.

The governing rule remains:

**LLM proposes. Software verifies. Evidence proves. Human approves.**

---

## Current Objective

Complete the Project Proposal using the current verified evidence artifacts.

Target flow:

`approved thesis topic`

→ bounded research discovery

→ deterministic verification planning

→ scholarly verification

→ official primary-source verification

→ verified evidence artifacts

→ proposal research synthesis

→ deterministic synthesis validation

→ adversarial proposal critique

→ proposal writing

→ deterministic proposal validation

→ DOCX rendering

→ human review

Missing evidence must remain explicit. The proposal must weaken, qualify, or remove unsupported claims instead of forcing them into a supported state.

The current deadline makes bounded completion more important than expanding the research architecture.

---

## Approved Thesis Topic

**A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring**

Topic selection is complete for the current proposal workflow.

Dataset, model, XAI-method, metric, legal-criterion, and experiment choices remain research decisions and must not be silently inherited from earlier manual drafts.

---

## Completed Capabilities

### Project Foundation

* Python 3.12 runtime managed through `uv`.
* `./scripts/uv` is the canonical project runner.
* Pydantic validates domain artifacts.
* `PROJECT.md`, `AGENTS.md`, `ARCHITECTURE.md`, and `CURRENT_STATE.md` are established.
* ADR process exists under `docs/decisions/`.
* Claude is the default LLM family for autonomous reasoning agents.
* Repository state is canonical project memory.
* Branch → pull request → human review → merge is the default workflow.
* Pull requests targeting `main` must update `CURRENT_STATE.md`.
* `.github/workflows/current-state-gate.yml` enforces that invariant.

### Scholarly Discovery and Verification

* OpenAlex scholarly discovery integration is implemented.
* Crossref and DataCite DOI lookup are available behind a provider-independent registry boundary.
* Bibliographic identity verification is implemented.
* Verification states preserve conflict and insufficient-data outcomes.
* OpenAlex lexical and semantic search modes exist.
* Search planning is bounded.
* Discovery provenance is preserved.
* Discovery candidates are not treated as evidence.

### Source Text and Artifact Acquisition

* Full-text location resolution is separate from source identity.
* OpenAlex GROBID XML, cached PDF, original OA PDF, and scholarly landing locations are represented.
* GROBID XML is preferred when available.
* Artifact downloads are bounded and validated.
* Raw artifact bytes receive SHA-256 identity.
* OpenAlex content API authentication is supported.
* Credentials are not stored in provenance.

### Scholarly Document Normalization

* `NormalizedDocument`, `NormalizedSection`, and `NormalizedParagraph` are implemented.
* Scholarly normalization is versioned.
* GROBID TEI parsing is deterministic.
* Section structure and paragraph ordinals are stable within a normalization version.
* Upstream ambiguity is preserved rather than silently repaired.

### Exact Evidence Addressing

* `EvidenceAddress` and `EvidenceSpan` are implemented.
* Evidence identity includes artifact SHA-256, normalization version, paragraph ordinal, start offset, and exclusive end offset.
* Evidence text is re-resolved deterministically.
* Invalid artifact identity, normalization version, paragraph, or offset is rejected.
* LLMs never compute canonical evidence offsets.

### Retrieval

* One normalized paragraph is one canonical `RetrievalUnit`.
* BM25 is implemented as deterministic lexical retrieval.
* Semantic retrieval is implemented behind a provider-independent embedding boundary.
* Voyage `voyage-4` is the selected semantic retriever for evidence acquisition.
* Semantic ranking uses cosine similarity.
* Retrieval and evidence extraction are separate concerns.
* Context expansion does not change retrieval-hit identity.
* Reciprocal Rank Fusion was evaluated and is retained only as an audited negative experiment.
* Existing development and held-out benchmarks remain frozen.

### Evidence Acquisition Core

* `EvidenceRequirement` is implemented.
* Requirement kinds cover literature, legal, dataset, baseline, method, metric, feasibility, and contribution needs.
* Evidence-query planning is bounded.
* Context expansion is deterministic and bounded.
* Claude-backed extraction operates only over supplied bounded context.
* Evidence support states are:
    * `SUPPORTED`;
    * `PARTIAL`;
    * `NOT_SUPPORTED`;
    * `INSUFFICIENT_EVIDENCE`.
* Supporting proposals require exact quote candidates.
* Unsupported and insufficient proposals cannot fabricate supporting evidence.
* Exact quote verification is deterministic.
* Character offsets are computed by software.
* Verified evidence preserves exact provenance.

### Proposal Research Domain

* Proposal research dimensions include:
    * problem;
    * research gap;
    * research question;
    * dataset;
    * baseline;
    * method;
    * metric;
    * feasibility;
    * contribution;
    * risk;
    * deliverable.
* Research epistemic states are:
    * `SUPPORTED`;
    * `DERIVED`;
    * `ASSUMPTION`;
    * `UNKNOWN`.
* Supported and derived findings must reference evidence requirements.
* Assumptions and unknowns cannot masquerade as evidence-backed findings.
* Proposal research synthesis may use only the approved topic, supplied requirements, and verified evidence.
* Proposal research synthesis performs no new research.

### Proposal Critic

* An adversarial proposal critic is implemented.
* Critique severities are `BLOCKER`, `MAJOR`, and `MINOR`.
* Verdicts are `PASS`, `REVISE`, and `FAIL`.
* The critic checks unsupported claims about novelty, law, datasets, methods, baselines, metrics, feasibility, and contribution.
* `PASS` requires no remaining critique issues.
* `FAIL` requires at least one blocker.

### Proposal Writer

* Proposal writing is separate from research.
* The writer performs no new research.
* The writer requires critic approval.
* Proposal paragraphs distinguish evidence-backed material, proposed work, and limitations.
* Assumptions and unknowns cannot be presented as established facts.

---

## Proposal Research Completed

### Live Discovery

A bounded discovery pass was completed across five research objectives:

* legal and problem framing;
* dataset candidates;
* baselines and methods;
* evaluation metrics;
* feasibility, contribution, and limitations.

The discovery artifact contains 39 research leads from 97 provider citations.

These citations are discovery provenance only and are not verified research evidence.

The discovery stage should not be rerun before the current proposal unless a concrete blocker later requires it.

### Deterministic Verification Plan

Verification planning is deterministic and local.

The current plan contains 18 bounded verification tasks:

* 5 official legal / regulatory primary-source tasks;
* 3 dataset-primary tasks;
* 10 scholarly tasks.

Twenty-one lower-priority discovered leads were intentionally deferred.

### Scholarly Verification

The scholarly verification lane reuses the existing stack:

`OpenAlex`

→ bibliographic identity verification

→ full-text acquisition

→ GROBID normalization

→ BM25 prefilter

→ Voyage semantic retrieval

→ bounded context

→ Claude evidence proposal

→ deterministic exact-span verification

All ten planned scholarly tasks completed.

The current scholarly artifact contains seven `PARTIAL` results and three `INSUFFICIENT_EVIDENCE` results.

The scholarly lane is sufficient for the first proposal pass and should not be rerun before synthesis.

### Official EU Primary-Law Verification

Known EU legal instruments and CJEU cases are resolved deterministically by CELEX rather than using LLM web search for source location.

Preferred path:

`verification requirement`

→ deterministic CELEX resolution

→ Publications Office / Cellar primary content

→ deterministic normalization

→ SHA-256 artifact identity

→ BM25 / Voyage retrieval

→ Claude evidence proposal

→ deterministic exact-span verification

InfoCuria search/list shells are not accepted as evidence sources.

The five planned legal tasks now resolve to official EU primary sources and currently produce `PARTIAL` evidence rather than overstated full support.

Current verified legal coverage includes:

* SCHUFA / C-634/21 treatment of creditworthiness scores under Article 22;
* the condition that a third party draws strongly on the score;
* Dun & Bradstreet Austria / C-203/22 explanation content;
* Article 15(1)(h) explanation rights read with Article 22(3);
* CCD2 explanation and human-review language;
* the AI Act profiling carve-back for Annex III systems.

The legal lane is sufficient for the current proposal pass.

### Dataset Primary-Source Verification

Current seeded candidates are:

* FICO HELOC;
* UCI Statlog German Credit / South German Credit correction;
* Kaggle Home Credit Default Risk.

The first full primary-source pass left all three as `INSUFFICIENT_EVIDENCE`.

That result established a verification gap, not dataset unsuitability.

A bounded dataset-primary retry capability has now been implemented.

Known dataset families use deterministic canonical routes where possible:

* FICO-controlled challenge / newsroom sources for HELOC;
* UCI canonical pages for German Credit and the South German Credit correction;
* Kaggle canonical competition data / evaluation / rules pages for Home Credit.

Primary-source retrieval now searches both the verification question and the explicit `why_needed` criteria before semantic ranking.

The user has run the bounded dataset retry. Its final artifact is the next item to review before proposal synthesis.

No additional broad dataset-landscape stage is required before the current Project Proposal.

---

## Current Research Artifacts

The proposal workflow currently uses:

* `proposal_discovery.json`
* `proposal_verification_plan.json`
* `proposal_scholarly_evidence_v2.json`
* `proposal_primary_evidence_v3.json`

These are machine-readable inputs to proposal synthesis.

They are not themselves trusted prose.

---

## In Progress

**Review the completed dataset-primary retry artifact, then synthesize the Project Proposal.**

Bounded next sequence:

`final primary-evidence artifact`

→ proposal research synthesis

→ deterministic validation

→ one adversarial critic pass

→ at most one bounded correction pass if required

→ writer

→ deterministic proposal validation

→ DOCX rendering and visual inspection

→ human review

No new general discovery loop should be added before the current Project Proposal unless the critic identifies a blocker that cannot be resolved by weakening or removing a claim.

---

## Deferred Until After the Project Proposal

Unless required to resolve a true blocker, defer:

* broad dataset-landscape discovery beyond the seeded candidates;
* full empirical comparison across many datasets;
* final thesis dataset lock;
* model training;
* XAI execution;
* experiment implementation;
* statistical result analysis;
* final Claim Ledger population from experiment results;
* long-term provenance persistence;
* vector database selection;
* orchestration framework selection;
* experiment-tracking platform selection;
* execution sandbox design;
* observability stack;
* deployment architecture;
* PDF-only scholarly normalization improvements not needed by the current evidence set;
* first-class table, figure, and equation evidence nodes.

The proposal may describe these as planned work. It must not claim they are already complete.

---

## Active Decisions

### Confirmed

* Approved topic: `A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring`.
* Claude is the default LLM family for autonomous reasoning agents.
* LLM output is not factual evidence.
* Web search and provider citations are discovery, not evidence.
* Discovery, verification, retrieval, extraction, synthesis, criticism, and writing remain separate concerns.
* Researcher, Critic, and Writer are separate roles.
* Writer performs no new research.
* Missing evidence remains explicit.
* Evidence support states and research epistemic states are separate concepts.
* Raw artifacts use SHA-256 identity.
* Normalization algorithms are versioned.
* Exact evidence spans are deterministically verifiable.
* LLMs do not compute canonical evidence offsets.
* BM25 remains the deterministic lexical baseline.
* Voyage `voyage-4` remains the selected semantic retriever for evidence acquisition.
* Existing retrieval benchmarks remain frozen.
* Context expansion remains separate from ranking and retrieval identity.
* Agent fan-out, retries, searches, and provider calls remain bounded.
* Proposal verification planning is deterministic.
* Official EU legal sources are resolved deterministically when possible.
* A downloadable primary source does not by itself establish evidentiary support.
* Partial evidence remains `PARTIAL`.
* The proposal may contain explicit limitations and unknowns.
* The current proposal should be completed from the evidence already collected instead of opening a new broad research cycle.
* Dataset choice for final thesis experiments remains revisable after the proposal.
* German Credit is not automatically selected as the primary dataset merely because it is a seeded candidate.
* Human approval remains required for consequential research decisions.
* Every pull request targeting `main` updates `CURRENT_STATE.md`.

### Not Yet Decided

* final primary dataset for thesis experiments;
* whether companion datasets will be used;
* final predictive baseline set;
* final predictive model set;
* final XAI method set;
* final quantitative explanation-quality metric set;
* final experiment design;
* final statistical-analysis plan;
* exact thesis Claim Ledger schema;
* long-term provenance persistence representation;
* vector persistence;
* orchestration framework;
* experiment-tracking system;
* deployment architecture;
* final university policy position on generative-AI assistance and disclosure.

---

## Current Risks

### RISK-001 — Deadline-driven architecture expansion

The proposal can miss its deadline if every incomplete facet triggers a new subsystem.

**Mitigation:** complete the proposal from the current bounded evidence set; weaken or remove unsupported claims instead of opening new general research loops.

### RISK-002 — Model-generated false certainty

LLMs may make stronger claims than the evidence supports.

**Mitigation:** exact spans, explicit support states, deterministic validation, adversarial criticism, and human review.

### RISK-003 — Discovery/evidence confusion

Search results or provider citations may be mistaken for verified evidence.

**Mitigation:** only deterministically verified source artifacts may support evidence-backed findings.

### RISK-004 — Full-text availability

Relevant scholarly sources may not expose usable full text.

**Mitigation:** preserve `INSUFFICIENT_EVIDENCE`; do not chase providers without a bounded reason.

### RISK-005 — Primary-source access variability

Official and dataset-provider sites may return redirects, shells, rate limits, or inconsistent content formats.

**Mitigation:** deterministic authority policy, bounded retries, canonical endpoints, artifact hashes, and explicit fetch failures.

### RISK-006 — Legal overclaiming

A judgment or regulation may support only part of a broad requirement.

**Mitigation:** preserve `PARTIAL`; proposal prose may use only the supported facet.

### RISK-007 — Dataset representativeness

A benchmark may be old, small, synthetic, weakly documented, or unrepresentative of modern consumer credit.

**Mitigation:** keep final dataset selection provisional where evidence does not justify a lock.

### RISK-008 — German Credit age and coding history

German Credit is historically important but old, small, and associated with coding/version issues.

**Mitigation:** distinguish original Statlog from the South German Credit correction and do not equate historical benchmark popularity with modern representativeness.

### RISK-009 — External API cost and instability

Anthropic, Voyage, OpenAlex, and other providers may fail or consume paid quota.

**Mitigation:** classify remote runs explicitly, run local preflight before paid retries, checkpoint long runs, and avoid blind reruns.

### RISK-010 — Documentation drift

Repository prose may lag behind runtime state.

**Mitigation:** runtime and tests are authoritative; update `CURRENT_STATE.md` at checkpoints.

### RISK-011 — Proposal over-specification

The proposal may present planned experiments or dataset choices as if they had already been empirically validated.

**Mitigation:** separate completed research, proposed methodology, expected contribution, and limitations.

---

## Known Unknowns

1. Final primary dataset or dataset combination.
2. Final predictive baselines and model families.
3. Final XAI methods.
4. Final quantitative explanation-quality metrics.
5. Exact translation from legal explanation requirements to measurable empirical criteria.
6. Final experimental design.
7. Final statistical-analysis plan.
8. Availability and appropriateness of sensitive attributes for fairness-oriented analysis.
9. Exact dataset limitations around provenance, licensing, age, and representativeness.
10. Current formal university policy for generative-AI assistance and disclosure.
11. Final thesis research questions after synthesis and critique.
12. Final contribution scope.
13. Final implementation and reproducibility plan.
14. Final Claim Ledger schema.

These unknowns do not all need to be eliminated before the Project Proposal.

---

## Next Actions

1. Review the completed dataset-primary retry artifact.
2. Preserve the five verified legal results already present in the primary evidence artifact.
3. Do not rerun broad scholarly discovery or the full scholarly verification lane before synthesis.
4. Combine final primary evidence with `proposal_scholarly_evidence_v2.json`.
5. Run proposal research synthesis using only the approved topic, verification requirements, and verified evidence.
6. Deterministically validate every evidence-backed finding.
7. Run one adversarial proposal critic pass.
8. Resolve critic issues by weakening, qualifying, or removing unsupported claims; use at most one bounded correction pass.
9. Do not open a new broad research loop unless an unresolved blocker makes the proposal invalid.
10. Run the writer only after critic approval.
11. Validate that evidence-backed prose points only to supported or partially supported findings.
12. Produce the final DOCX.
13. Render and visually inspect the DOCX.
14. Human-review title, research questions, dataset strategy, methodology, evaluation, contribution, limitations, and references.
15. Submit the Project Proposal.

---

## Current Milestone Exit Criteria

The Project Proposal milestone is complete when:

* the approved topic is explicit;
* proposal research findings are derived from verified evidence;
* legal framing is grounded in official primary sources;
* dataset strategy is evidence-backed or explicitly qualified as provisional;
* baselines, methods, and metrics are justified from verified scholarly evidence or clearly labelled as proposed;
* unsupported novelty claims are absent;
* unsupported legal-compliance claims are absent;
* unresolved evidence gaps appear as limitations;
* the critic returns `PASS`;
* the writer performs no new research;
* final proposal prose passes deterministic validation;
* the DOCX renders correctly;
* a human has reviewed the final proposal;
* the proposal is submitted.

---

## Runtime Authority

Repository documentation is project memory, but executable behavior and tests are authoritative.

Before committing this checkpoint:

1. run the full deterministic suite with `./scripts/uv run pytest`;
2. record no exact passing-test count unless it comes from the current runtime;
3. inspect `git status --short`;
4. verify that secrets or credentials are not staged;
5. commit `CURRENT_STATE.md` together with the implementation changes that produced this state.
