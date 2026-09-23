Thesis Factory
==============

1\. Purpose
-----------

Thesis Factory is an auditable AI-assisted research and software-engineering system designed to support the production of a master's thesis in Computer Science with a FinTech focus.

The project is not intended to be a system that simply asks a large language model to generate a thesis.

Instead, it aims to create a reproducible workflow in which research, evidence collection, software development, experimentation, academic writing, review, and human approval are treated as explicit stages with traceable artifacts.

The system should make it possible to determine where an important statement, research conclusion, experimental result, citation, or software artifact came from and how it was verified.

2\. Project Context
-------------------

The final academic deliverable is a master's thesis in Computer Science in a FinTech-related area.

The exact thesis topic, research question, methodology, dataset, experimental design, and expected scientific contribution have not yet been selected.

The first substantive objective of the project is therefore not thesis writing.

It is to identify and validate a researchable thesis topic based on available academic literature, data, technical feasibility, measurable evaluation criteria, and an appropriate master's-level research contribution.

3\. Primary Goal
----------------

Build a system capable of supporting the following lifecycle:

1.  Discover and evaluate potential research topics.

2.  Search for relevant academic literature.

3.  Verify bibliographic sources.

4.  Extract evidence from primary sources.

5.  Identify potential research gaps.

6.  Formulate research questions and hypotheses.

7.  Design reproducible experiments.

8.  Implement the required software.

9.  Execute and record experiments.

10.  Analyse results.

11.  Produce evidence-backed academic writing.

12.  Audit claims, citations, methodology, and conclusions.

13.  Require human approval at important decision points.

14.  Produce the final thesis and supporting research artifacts.


The system should evolve incrementally. A capability should be implemented when a concrete requirement justifies it rather than because a technology or framework is available.

4\. Non-Goals
-------------

Thesis Factory is not intended to:

*   treat an LLM as an authoritative factual source;

*   generate an entire thesis from a single prompt;

*   hide uncertainty or unsupported claims behind fluent language;

*   automatically accept AI-generated research conclusions;

*   replace human responsibility for academic decisions;

*   introduce technologies solely for architectural complexity;

*   optimise for maximum autonomy at the expense of auditability;

*   assume that model output is correct because multiple agents agree with each other.


5\. Core Principles
-------------------

### 5.1 Evidence over model memory

Statements about external reality must not be accepted solely because an LLM generated them.

Where verification is possible, claims should ultimately be supported by appropriate evidence such as academic sources, authoritative documentation, executable code, tests, datasets, or experiment outputs.

### 5.2 Repository over conversation memory

The Git repository is the canonical source of truth for project state.

Chat conversations and model memory may provide useful context, but they must not override the current repository state.

If conversation context conflicts with the repository, the repository wins.

### 5.3 Explicit epistemic state

Important information should be distinguishable as one of:

*   **VERIFIED** — supported by an identified source, artifact, test, or experiment;

*   **DERIVED** — logically derived from verified information;

*   **ASSUMPTION** — deliberately accepted without complete verification;

*   **UNKNOWN** — not currently known.


Unknown information should remain explicitly unknown rather than being completed by plausible model-generated content.

### 5.4 Verification before acceptance

Important artifacts should have an appropriate verification mechanism.

Examples include:

*   academic claims checked against source evidence;

*   citations checked against real bibliographic records;

*   code checked by execution and automated tests;

*   experiment results linked to recorded configuration and inputs;

*   architectural assumptions documented and reviewed.


### 5.5 Prefer deterministic software where possible

LLMs should be used where language understanding, synthesis, planning, or reasoning is genuinely required.

Tasks that can be reliably implemented using deterministic software should normally not be delegated to an LLM.

Examples include schema validation, identifier resolution, test execution, file hashing, build processes, and structural validation.

### 5.6 Human authority

AI systems may research, propose, implement, analyse, critique, and review.

The human project owner retains authority over consequential decisions such as:

*   thesis topic selection;

*   research question approval;

*   methodology approval;

*   interpretation of major findings;

*   architectural decisions with significant consequences;

*   acceptance of thesis milestones;

*   final academic submission.


### 5.7 Reproducibility

Research and experiments should be reproducible whenever reasonably possible.

The project should preserve sufficient information to reconstruct important results, including relevant code, configuration, inputs, model information, source provenance, and experiment outputs.

### 5.8 Auditability

The system should favour designs that make its behaviour inspectable.

For important outputs, it should be possible to answer questions such as:

*   Why was this claim made?

*   Which evidence supports it?

*   Which source produced that evidence?

*   Which version of the code produced this result?

*   Which model or process produced this artifact?

*   Which verification steps were performed?

*   Who approved the result?


6\. Human and AI Responsibilities
---------------------------------

### Human Project Owner

The human project owner acts as the research director and final decision maker.

Responsibilities include:

*   defining project constraints;

*   approving major research directions;

*   reviewing important artifacts;

*   resolving ambiguous or contested decisions;

*   ensuring compliance with university requirements;

*   accepting or rejecting major milestones;

*   taking responsibility for the final academic work.


### AI Agents

AI agents may eventually perform specialised tasks including:

*   research planning;

*   literature discovery;

*   evidence extraction;

*   research criticism;

*   experiment design;

*   software engineering;

*   result analysis;

*   academic drafting;

*   methodological review;

*   claim auditing.


The exact set of agent roles has not yet been finalised.

Agent responsibilities and permissions must be explicitly defined rather than inferred from conversational context.

7\. Model Strategy
------------------

Claude models accessed through the Anthropic API are the required default LLM family for autonomous reasoning agents in Thesis Factory.

However, the core project architecture should not depend directly on Anthropic-specific APIs.

Model access should eventually be placed behind an internal abstraction so that:

*   agent logic is separated from provider-specific integration;

*   model configuration can be changed centrally;

*   tests can substitute mock or deterministic model implementations;

*   controlled model comparisons remain possible in the future.


This requirement does not imply that every AI-related component must use Claude.

Non-generative components such as parsers, embedding models, databases, search systems, validators, and deterministic tools may use other technologies when justified by their requirements.

8\. Current Unknowns
--------------------

The following items are intentionally unresolved:

*   final thesis topic;

*   final research question;

*   scientific hypothesis;

*   research methodology;

*   required dataset or datasets;

*   availability and licensing of required data;

*   experimental design;

*   evaluation metrics;

*   exact expected academic contribution;

*   university thesis formatting requirements;

*   citation style;

*   thesis length requirements;

*   university policy regarding AI-assisted research and writing;

*   submission deadline and intermediate academic deadlines;

*   final agent topology;

*   orchestration framework;

*   persistence architecture;

*   retrieval architecture;

*   observability stack;

*   experiment tracking infrastructure;

*   deployment model.


These items must not be silently converted into assumptions.

When one of them is resolved, the corresponding canonical project artifact should be updated.

9\. Success Criteria
--------------------

The project will be considered successful when it can demonstrate that:

1.  A defensible and researchable master's thesis topic has been selected.

2.  Important academic sources used by the thesis can be independently identified and verified.

3.  Material factual claims can be traced to appropriate evidence.

4.  The research methodology is explicitly documented.

5.  Software and experiments required by the research can be reproduced from recorded artifacts.

6.  Experiment results are preserved with sufficient provenance to support the thesis conclusions.

7.  The final academic text does not rely on fabricated citations or knowingly unsupported claims.

8.  Important AI-generated outputs pass defined review or validation steps before acceptance.

9.  Major research decisions have explicit human approval.

10.  The final thesis can be built together with its supporting bibliography, research artifacts, software, and experimental results.


10\. Current Project Phase
--------------------------

**Phase 0 — Project Foundation**

Current objectives:

*   establish canonical project documentation;

*   define how architectural decisions are recorded;

*   define operating rules for humans and AI agents;

*   establish a reliable representation of current project state;

*   identify university and academic constraints;

*   design the first researchability workflow.


No application architecture or implementation framework is considered final at this stage.

11\. Continuous Validation and Failure Discovery
------------------------------------------------

The project does not assume that all failure modes can be identified during initial design.

Instead, Thesis Factory should be designed to discover errors incrementally and as early as possible.

Important intermediate artifacts should be validated before they are incorporated into larger downstream artifacts.

Where practical, newly discovered failure modes should be converted into reusable safeguards such as:

*   deterministic validation rules;

*   automated tests;

*   evaluation cases;

*   reviewer checks;

*   architectural invariants;

*   documented failure categories.


The preferred lifecycle is:

**failure discovered → failure classified → safeguard implemented → regression evaluation added**

The system should therefore improve its ability to detect previously observed classes of errors over the lifetime of the project.

Final thesis review is a last line of defence, not the primary mechanism for establishing correctness.

12\. Bounded Agent Execution
----------------------------

Autonomous verification, research, review, and correction loops must be explicitly bounded.

Thesis Factory must not assume that additional agent iterations necessarily produce better results.

Every autonomous workflow should eventually define appropriate resource limits, which may include:

*   maximum iteration count;

*   maximum model calls;

*   maximum token budget;

*   maximum number of parallel agents;

*   maximum external searches or tool calls;

*   maximum retry count.


Agents must not recursively create additional agents without orchestration-level approval.

A workflow should terminate or escalate to a human when:

*   its execution budget has been exhausted;

*   repeated iterations produce no meaningful new information;

*   the same unresolved issue repeatedly reappears;

*   available evidence is insufficient to resolve the question;

*   agents disagree without a deterministic or evidential method of resolving the disagreement;

*   continuing execution has an unjustified expected cost.


Uncertainty is an acceptable terminal state.

The system should prefer an explicit **UNKNOWN**, **CONTESTED**, or **HUMAN\_REVIEW\_REQUIRED** state over unlimited autonomous attempts to manufacture certainty.

Human review acts both as a decision authority and as a circuit breaker for non-converging agent workflows.

Resource efficiency is a system quality attribute alongside correctness, auditability, and reproducibility.