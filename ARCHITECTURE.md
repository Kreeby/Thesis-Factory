# Thesis Factory Architecture

Status: INITIAL CONCEPTUAL ARCHITECTURE
Last updated: 2026-09-23

## 1. Purpose

This document describes the current architecture of Thesis Factory at the level that is justified by known project requirements.

It intentionally distinguishes architectural concepts from implementation choices.

Technologies, frameworks, storage engines, orchestration systems, and deployment mechanisms are not considered selected unless an accepted ADR explicitly establishes them.

---

## 2. Architectural Objective

Thesis Factory is designed as an auditable research and software-engineering system that transforms uncertain research questions into progressively more verified artifacts.

The system should support a lifecycle broadly resembling:

```text
research question
        ↓
literature discovery
        ↓
source verification
        ↓
evidence extraction
        ↓
claims / research gap
        ↓
hypothesis
        ↓
experiment design
        ↓
software implementation
        ↓
experiment execution
        ↓
results
        ↓
academic argument
        ↓
thesis artifact
```

Each transition should preserve enough provenance to explain how downstream outputs were produced.

---

## 3. Architectural Principle: Artifacts Before Prose

The primary internal representation of the research process should not be the final thesis document.

The thesis document is a presentation artifact produced from smaller research and engineering artifacts.

Examples of such artifacts may include:

* research questions;
* source records;
* evidence records;
* claims;
* hypotheses;
* experiment specifications;
* software versions;
* experiment runs;
* results;
* review findings;
* approval records.

Where practical, larger artifacts should be constructed only after smaller dependencies have been sufficiently validated.

---

## 4. Conceptual System Boundaries

The system is currently divided conceptually into the following responsibilities.

### 4.1 Orchestration

Coordinates workflow execution.

Responsibilities may eventually include:

* task sequencing;
* state transitions;
* agent invocation;
* execution budgets;
* retries;
* failure handling;
* human-review gates;
* workflow termination.

The implementation technology is not yet selected.

### 4.2 Research

Responsible for discovering and analysing scholarly information.

Potential responsibilities include:

* query planning;
* literature discovery;
* bibliographic verification;
* evidence extraction;
* contradiction discovery;
* research-gap analysis;
* hypothesis formation.

Research output should preserve source provenance.

### 4.3 Engineering

Responsible for software and computational work required by the research.

Potential responsibilities include:

* implementation;
* tests;
* experiment tooling;
* data processing;
* reproducible execution;
* build artifacts.

Software output should be traceable to version-controlled code.

### 4.4 Experimentation

Responsible for transforming research hypotheses into reproducible empirical results.

Potential responsibilities include:

* experiment specification;
* configuration;
* dataset references;
* run execution;
* metric calculation;
* result storage;
* provenance recording.

Experiment results must not be represented as verified merely because an LLM generated or interpreted them.

### 4.5 Academic Synthesis

Responsible for transforming verified research and experimental artifacts into academic prose.

Potential responsibilities include:

* outline construction;
* section drafting;
* argument synthesis;
* citation placement;
* result interpretation.

Academic synthesis must operate on traceable project artifacts rather than unrestricted model memory whenever evidence is required.

### 4.6 Verification and Audit

Responsible for detecting unsupported, inconsistent, contradictory, or invalid outputs.

Verification may include both deterministic software and AI-assisted review.

Examples include:

* bibliographic validation;
* source-to-claim verification;
* test execution;
* schema validation;
* experiment provenance checks;
* contradiction detection;
* methodological review;
* cross-document consistency review.

### 4.7 Human Governance

The human project owner remains outside autonomous execution loops and acts as the authority for consequential decisions.

Human intervention may occur when:

* a research direction must be selected;
* evidence remains inconclusive;
* agents fail to converge;
* architectural decisions are required;
* execution budgets are exhausted;
* academic judgment is necessary;
* a milestone requires explicit approval.

---

## 5. High-Level Information Flow

A simplified conceptual flow is:

```text
                    HUMAN PROJECT OWNER
                           │
                    goals / approvals
                           │
                           ▼
                     ORCHESTRATION
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      RESEARCH        ENGINEERING      EXPERIMENTATION
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                  VERIFIED ARTIFACTS
                           │
                           ▼
                  ACADEMIC SYNTHESIS
                           │
                           ▼
                       AUDIT
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
               PASS              REJECT /
                                  ESCALATE
                 │
                 ▼
                    THESIS ARTIFACT
```

This diagram represents responsibility boundaries rather than deployed services.

No requirement currently exists for these components to be separate processes or applications.

---

## 6. Trust Model

Different outputs have different trust levels.

A useful conceptual ordering is:

```text
LLM-generated output
        ↓
structured artifact
        ↓
independent review
        ↓
deterministic validation where possible
        ↓
source / test / experiment evidence
        ↓
human approval where required
```

This is not a universal linear pipeline.

Different artifact types may require different verification paths.

The fundamental rule is that generation and verification are separate concerns.

---

## 7. Provenance

Important downstream artifacts should preserve links to the artifacts from which they were derived.

Examples:

```text
claim
  → evidence
      → source
```

```text
result
  → experiment run
      → experiment specification
          → code version
          → configuration
          → dataset version
```

```text
thesis paragraph
  → claims
      → supporting evidence
```

The exact persistence model for provenance is not yet selected.

---

## 8. Agent Architecture

The exact agent topology is not yet finalised.

Current architecture assumes that specialised reasoning roles may exist, but their boundaries will be introduced only when required by executable workflows.

Potential roles include:

* research planner;
* literature researcher;
* research critic;
* experiment designer;
* software engineer;
* academic writer;
* auditor.

These are conceptual roles, not yet implemented services or classes.

Autonomous reasoning agents use Claude models by default in accordance with ADR-0001.

Agents should receive task-scoped context and minimum necessary permissions.

The orchestration layer, rather than individual agents, should ultimately control workflow-level execution budgets and agent spawning.

---

## 9. Deterministic Components

Where reliable deterministic implementation is possible, the system should prefer software over generative reasoning.

Likely examples include:

* schema validation;
* file hashing;
* identifier validation;
* bibliography metadata resolution;
* test execution;
* build processes;
* experiment execution;
* resource-budget accounting;
* repository state inspection.

The exact tools and implementations remain undecided.

---

## 10. Failure Handling

Failures should be represented explicitly rather than hidden by automatic retries.

Conceptual terminal states may include:

* `COMPLETED`
* `FAILED`
* `UNKNOWN`
* `CONTESTED`
* `BLOCKED`
* `HUMAN_REVIEW_REQUIRED`
* `BUDGET_EXHAUSTED`

Autonomous retry loops must be bounded.

Repeated non-progress should result in termination or human escalation rather than unlimited model execution.

---

## 11. Validation Strategy

Validation should occur incrementally.

Preferred direction:

```text
small artifact
    ↓
validation
    ↓
larger artifact
    ↓
validation
    ↓
larger artifact
```

The project should avoid depending primarily on a final review of the complete thesis.

Newly discovered meaningful failure modes may later become:

* regression tests;
* evaluation cases;
* validation rules;
* documented invariants;
* reviewer checks.

---

## 12. Model Boundary

Claude is the default reasoning-model family.

Provider-specific API concerns should be isolated from project domain logic where reasonably practical.

Conceptually:

```text
agent / reasoning component
          ↓
     model boundary
          ↓
   Anthropic / Claude
```

The exact interface has not yet been designed.

No generic multi-provider framework is required at this stage.

---

## 13. Persistence

The project will require persistent state for some combination of:

* workflow state;
* research sources;
* evidence;
* claims;
* experiment metadata;
* provenance;
* evaluation results;
* model-execution metadata.

The persistence architecture is intentionally unresolved.

No database technology has been selected.

---

## 14. External Integrations

The project is expected to require external systems for tasks such as:

* scholarly literature discovery;
* bibliographic metadata verification;
* model access;
* source retrieval;
* code hosting;
* potentially experiment infrastructure.

Specific APIs and integration protocols will be selected only when required by an executable workflow.

---

## 15. Security and Isolation

The project may eventually execute generated or AI-modified code.

Such execution must not be assumed safe.

Before autonomous code execution is introduced, the project must explicitly design appropriate isolation, filesystem access, network permissions, secret handling, and execution limits.

No execution-sandbox architecture has yet been selected.

---

## 16. Current Non-Decisions

The architecture currently does **not** select:

* LangGraph or another orchestration framework;
* FastAPI or another API framework;
* PostgreSQL or another database;
* pgvector or another vector system;
* MCP or another tool protocol;
* Temporal or another durable-execution framework;
* MLflow or another experiment tracker;
* a deployment platform;
* a frontend framework;
* a concrete agent topology;
* a concrete provenance schema;
* a concrete claim-ledger schema;
* a concrete evaluation framework.

These remain implementation candidates only.

---

## 17. Architecture Evolution

Architecture should evolve from executable requirements.

The preferred sequence is:

```text
requirement
    ↓
minimal design
    ↓
implementation
    ↓
evaluation
    ↓
observed limitation
    ↓
architectural change when justified
```

Architecture should not grow solely from hypothetical future requirements.

Significant architectural decisions should be recorded using ADRs.
