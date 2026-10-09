# Current Project State

## Post-merge continuation (2026-10-09)

PR #16 has been merged into `main`. The user reported **207 passing local
pytest tests** on its final head. Earlier references below to PR #16 being
unmerged and its pre-merge test status are historical review snapshots.

The long-term product objective is a single bounded, auditable run that can
research the approved credit-scoring XAI topic, perform reproducible thesis
experiments, prepare a complete draft, and independently critique its claims.
It must preserve all intermediate evidence and permit explicit human gates.
**A ten-hour end-to-end thesis orchestrator is not yet implemented.**

Next incremental slice: offline research JSON checkpointing, stage-level
append-only logging, model-usage event API, and human-reviewable intermediate
PR preparation. See `docs/architecture/autonomous-thesis-workflow.md`.

Last updated: 2026-10-09

## Current Phase

**Phase 1 — Evidence Acquisition and Proposal Research — PR #16 under review (unmerged)**

Phase 0 — Project Foundation — is complete.

The approved thesis topic is:

`A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring`

The retrieval architecture comparison cycle is complete for the current Phase 1 scope. Voyage `voyage-4` remains the selected default semantic retriever for evidence acquisition, with BM25 retained as the deterministic lexical baseline and diagnostic comparator.

The system now supports bounded proposal-oriented research from an approved topic through discovery, verification, exact evidence extraction, research synthesis, adversarial critique, and proposal writing.

The immediate objective is to review and integrate PR #16 safely. A Project Proposal DOCX has already been generated outside the repository through a deadline-specific direct writer invocation; formal university submission is not confirmed. The normal Critic-to-Writer production pipeline was not completed.

The governing rule remains:

**LLM proposes. Software verifies. Evidence proves. Human approves.**

---

## Current Objective

Complete an engineering review of [PR #16](https://github.com/Kreeby/Thesis-Factory/pull/16), branch `phase1/evidence-acquisition` targeting `main`, before merging. This PR currently consists of 3 commits, 67 changed files and about 12,657 added lines. The branch contains source implementations and unit tests for acquisition, scholarly and primary source verification, research synthesis, Critic and Writer. It already contains a `CURRENT_STATE.md` change, but its existing content incorrectly describes the proposal as unfinished and some gates as passed.

1. Run the **full local deterministic test suite on the exact PR head**; current GitHub Actions only verifies that `CURRENT_STATE.md` changed, not test success.
2. Review new source trust boundaries, exact span claims, error handling, bounded API cost and coverage.
3. Preserve the actual proposal artifacts and the history of merged Phase 1 retrieval benchmarks without pretending the deadline-specific proposal was produced through a fully validated end-to-end pipeline.
4. Address merge blockers; retain later research improvements as explicit next steps rather than expanding this PR indefinitely.

The governing rule remains **LLM proposes. Software verifies. Evidence proves. Human approves.**

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

The bounded dataset retry completed. Final primary results: 5 legal tasks PARTIAL, German Credit dataset task PARTIAL (2 exact spans), FICO HELOC and Home Credit INSUFFICIENT_EVIDENCE. Legal verification had 11 exact spans; scholarly verification had 16. Across 18 verification tasks: 13 PARTIAL, 5 INSUFFICIENT_EVIDENCE and 29 exact spans. These statuses are not evidence of full support for each broad requirement.

No additional broad dataset-landscape stage is required before the current Project Proposal.

---

## Current Research Artifacts

The recorded proposal workflow uses:

* `proposal_discovery.json`
* `proposal_verification_plan.json`
* `proposal_scholarly_evidence_v2.json`
* `proposal_primary_evidence_v3.json`

These are machine-readable inputs to proposal synthesis.

They are not themselves trusted prose.

---

## PR #16 — Verified Implementation and Research Checkpoint

**PR facts as observed on GitHub, 2026-10-09:** `main` base `26701a0`; head `e2b2775`; 3 commits (`2bd80bb`, `c79866f`, `e2b2775`); 67 changed files; open and unmerged. The PR does include `CURRENT_STATE.md`. The GitHub Actions `Current State Gate` ran successfully and checks only that this file was changed. Full suite status on the exact head remains unknown.

### Code implemented in the branch

* **Evidence requirements and extraction:** `domain/evidence_acquisition.py`, `evidence/context.py`, `evidence/extraction.py`. Typed evidence states, bounded queries and contexts, quote proposals, exact source spans and deterministic address verification. A citation reference is not proof of semantic entailment.
* **Research roles:** `domain/proposal_research.py`, `research/proposal_research.py`, `research/proposal_critique.py`, `research/proposal_writing.py`. SUPPORTED, DERIVED, ASSUMPTION and UNKNOWN are epistemically distinct. Critic supports PASS/REVISE/FAIL. The writer's normal API requires PASS.
* **Web discovery and planning:** Anthropic web research, lead extraction, bounded deterministic verification planning and scripts. Web citations are discovery provenance only.
* **Scholarly acquisition:** OpenAlex bibliographic identity and GROBID full text, BM25/Voyage retrieval, exact verified extraction and bounded scholarly verification executor.
* **Primary source acquisition:** deterministic legal CELEX candidate routing; Publications Office/Cellar primary-source content, HTML/XHTML/XML normalization, source authority host policy, source audit and SHA-256 identities. Canonical dataset URLs for FICO HELOC, UCI German/South German Credit and Kaggle Home Credit are seeded candidates, **not a landscape search**.
* **Checkpointed CLI scripts:** research discovery, verification planner, scholarly verification, primary verification and dataset retry. Dataset retry preserves previous primary task results and replaces insufficient dataset tasks.
* **Tests:** domain, context, extraction, model integration, legal source routing, fetch and normalization, planners, scholarly and primary executors, proposal research, Critic and Writer have test files in the PR. Earlier local reports: 153 passed after evidence core, 162 passed after research contracts; another later development run reported 201 passed / 1 stale assertion failed and a focused correction test. These are historical snapshots, not proof that the final head's full test suite passes.

### Real research artifacts — live run outcomes, outside this PR

* **Discovery:** 5 bounded objectives, 97 citations, 39 leads. Citations were discovery-only.
* **Plan:** 18 tasks (5 official legal, 3 dataset-primary, 10 scholarly), 21 leads deferred.
* **Scholarly:** 10 task results, 7 PARTIAL / 3 INSUFFICIENT_EVIDENCE, 30 usable full texts and 16 exact spans. Outstanding specific gaps include HELOC baseline performance, preprocessing details and out-of-time validation.
* **Official legal:** 5 PARTIAL, 11 exact spans from SCHUFA C-634/21, Dun & Bradstreet Austria C-203/22, GDPR discussion, CCD2 recital and AI Act profiling text. Other aspects (CCD2 operative Art. 18(8), Annex III 5(b) and fraud exclusion, broad legal extension claims) are not verified by the selected spans.
* **Datasets:** German Credit PARTIAL with two exact UCI snippets distinguishing original categorical `german.data` and edited indicator-file; FICO HELOC and Home Credit INSUFFICIENT_EVIDENCE. No final dataset selection is justified.
* **Aggregate:** 18 tasks; 13 PARTIAL, 5 INSUFFICIENT_EVIDENCE, 29 verified exact spans. These numbers do not mean all legal/dataset questions were answered.
* **Synthesizer:** `proposal_research_draft.json` produced and structurally validated, acknowledging unproven research gap, provisional model choices, no final dataset and non-compliance claims.
* **Critic:** live response truncated into invalid JSON; no validated verdict or critique artifact. Human explicitly skipped Critic rather than fabricating findings or PASS.
* **Document:** direct one-off structured writer call, document structural validation and external DOCX render succeeded. Not reproducible through an integrated renderer in PR #16. University submission remains unconfirmed.

### Engineering review findings (require prioritization, not fabricated fixes)

1. `validate_research_draft` checks evidence IDs/status/spans but **does not guarantee semantic support** for generated claims. `validate_proposal_document` checks finding references and paragraph class, not external truth, complete citation bibliographies or legal compliance.
2. Critic's large structured output can truncate and cause parsing errors. Never spend more API tokens on blind retries; add local fake-client/size tests before a future targeted fix.
3. Primary executor's bounded `max_documents` and ranking of a **single best result** can omit complementary partial evidence across sources. PARTIAL and INSUFFICIENT_EVIDENCE must remain visible.
4. Host allowlists establish authority of domain but do not establish that the fetched content proves the requirement. HTTP 503, HTML shells and rate limits can cause legitimate verification gaps.
5. Seeded three-dataset canonical routing cannot be treated as a comprehensive autonomous search and evaluation of all candidate datasets.
6. Preserving the old `CURRENT_STATE.md` evaluation history matters: earlier abbreviated replacement removed many exact historical retrieval benchmark measurements. This document keeps current capabilities and the decision not to retune frozen benchmarks, but that earlier detailed historical measurement record remains retrievable from `main` before merge and should be preserved durably.
7. `PROJECT.md` still contains older phase/unknowns language; align after the feature PR is reviewed. Do not silently invent or rewrite ADRs.

### Outstanding decisions after integration

Final research gap; dataset and licence strategy; feature provenance and representativeness; model/baseline/XAI selection; preprocessing and split; technical explanation-quality and calibration metrics; legal-to-metric mapping without compliance claims; empirical evaluation and statistical design; Claim Ledger; provenance storage and end-to-end artifact generation; scalable but bounded agent exploration; formal university AI policy. None of these are complete just because a proposal draft exists.

---

## In Progress

**PR #16 review and merge readiness.** No new source discovery or Anthropic/Voyage calls are necessary to complete this checkpoint.

The recorded live research run produced `proposal_research_draft.json` with 31 findings and passed the structural validator. The Critic call failed because the generated JSON was truncated (Pydantic EOF while parsing around column 8160). **No valid Critic result or verdict was produced**. The beginning of the invalid output mentioned `REVISE`, but this is not a parsed/validated verdict.

The human expressly rejected fabricating a critique or a fake `PASS` and authorized skipping Critic for the immediate deadline. An isolated direct call to `AnthropicStructuredReasoner.generate` produced `proposal_document_draft.json`; `validate_proposal_document` passed. A DOCX Project Proposal was then generated separately from the repository. **Normal `ProposalWriter.write` still requires a genuine Critic `PASS`, and PR #16 contains no integrated human-override workflow or DOCX exporter.**

Formal proposal submission is not confirmed. Dataset selection, novelty, research gap and experimental feasibility remain provisional. No empirical thesis experiments have been conducted.

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

The earlier proposal deadline exposed the risk that every incomplete research facet triggers a new subsystem.

**Mitigation:** scope new architecture against measured blockers, preserve provenance, and treat existing proposal output as a historical checkpoint.

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

1. Review [PR #16](https://github.com/Kreeby/Thesis-Factory/pull/16) at head `e2b277528dbeeb671f6e8f82797333c47376c808` and verify full `./scripts/uv run pytest` result locally (**FREE / LOCAL**). Earlier checkpoint test counts are not a current-head test result.
2. Inspect the complete diff for correctness, provenance, unsafe secret handling and unintended checked-in research artifacts. The only GitHub Actions run observed for the PR is the passing `Current State Gate`; it does **not** run pytest.
3. Update `CURRENT_STATE.md` in the same feature branch; do not make fictional audit results or claim an integrated Critic-bypass implementation.
4. Keep canonical run artifacts (`proposal_discovery.json`, `proposal_verification_plan.json`, `proposal_scholarly_evidence_v2.json`, `proposal_primary_evidence_v3.json`, `proposal_research_draft.json`, `proposal_document_draft.json`) and the DOCX under controlled provenance if storage/versioning is explicitly chosen; they are not currently part of PR #16.
5. Preserve the existing held-out retrieval benchmark and `voyage-4` decision from PR #14 without retrospective tuning.
6. After human review and approval, merge the PR. Then consider a durable proposal workflow and careful dataset landscape comparison as **future** work, not accomplished PR functionality.

---

## Current Milestone Exit Criteria

**For this PR**, acceptance requires accurate documentation, a current full local test report, reviewed code and bounded provider calls, no accidental credentials/runtime outputs committed, known gaps clearly recorded, and explicit human review. A passing documentation gate alone is not sufficient.

The Project Proposal draft and DOCX were generated under an explicit deadline-specific decision to skip Critic. The integrated Critic→Writer PASS-gated path remains unverified, and formal submission has not been established.

---

## Runtime Authority

Repository documentation is project memory, but executable behavior and tests are authoritative.

Before committing this checkpoint:

1. run the full deterministic suite with `./scripts/uv run pytest`;
2. record no exact passing-test count unless it comes from the current runtime;
3. inspect `git status --short`;
4. verify that secrets or credentials are not staged;
5. commit `CURRENT_STATE.md` together with the implementation changes that produced this state.
