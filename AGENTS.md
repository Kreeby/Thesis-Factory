# Agent Operating Contract

This document defines the operating rules for AI agents working with the Thesis Factory repository.

These rules apply unless a more specific instruction exists for a particular component or task.

---

## 1. Repository Authority

The repository is the canonical source of truth for the project.

Agents must not rely on conversational memory when repository artifacts are available.

If conversation context, model memory, previous assumptions, or generated text conflict with the current repository state, the repository state takes precedence.

---

## 2. Required Bootstrap Context

Before performing substantial work, an agent must inspect the relevant current project state.

At minimum, when available, read:

1. `PROJECT.md`
2. `ARCHITECTURE.md`
3. `CURRENT_STATE.md`
4. relevant accepted ADRs under `docs/decisions/`
5. files directly related to the current task
6. relevant tests or evaluation artifacts

Agents should not load unrelated parts of the repository without a concrete reason.

Use the minimum context necessary to perform the task correctly.

---

## 3. Do Not Invent Missing Project State

If required information is unavailable, distinguish it explicitly as:

* **VERIFIED**
* **DERIVED**
* **ASSUMPTION**
* **UNKNOWN**

Do not silently convert an unknown into an assumption.

Do not infer missing requirements merely because a likely or conventional answer exists.

Examples:

* do not assume a university citation style;
* do not assume a thesis deadline;
* do not assume a dataset has been selected;
* do not assume a framework is approved because it was previously discussed;
* do not assume documentation matches runtime behaviour without verification.

---

## 4. Evidence and Verification

LLM-generated statements are not evidence.

When a claim can be verified using an authoritative source, executable artifact, test, dataset, experiment, or repository state, verification should be preferred over model memory.

For external factual claims, prefer primary or authoritative sources where reasonably available.

For code behaviour, prefer execution and tests over textual reasoning.

For repository behaviour, prefer current code over stale documentation.

For research claims, preserve provenance to the supporting evidence.

---

## 5. Minimal Change Principle

Agents should make the smallest coherent change required to satisfy the task.

Do not:

* rewrite unrelated files;
* refactor unrelated components;
* change architectural decisions opportunistically;
* introduce a new framework without a demonstrated requirement;
* create abstractions for hypothetical future use without justification.

If broader changes appear necessary, surface them separately rather than silently expanding the task.

---

## 6. Architectural Decisions

Significant architectural choices must not be introduced implicitly.

If a change creates or materially modifies a decision involving areas such as:

* orchestration;
* model providers;
* persistence;
* retrieval;
* research provenance;
* agent permissions;
* execution isolation;
* evaluation;
* external integrations;
* deployment;
* security;

the agent should determine whether an ADR is required.

Accepted ADRs remain authoritative until explicitly superseded by another decision.

Do not silently violate an accepted ADR.

---

## 7. Technology Selection

Do not treat previously discussed technologies as selected merely because they were mentioned.

Examples such as LangGraph, PostgreSQL, pgvector, MCP, FastAPI, Temporal, or MLflow remain candidates until the project explicitly adopts them.

Technology choices must follow requirements.

Prefer the simplest architecture that satisfies the current requirement while preserving important project invariants.

---

## 8. LLM Strategy

Claude models accessed through the Anthropic API are the required default LLM family for autonomous reasoning agents unless the project owner explicitly changes this decision.

Domain logic must not depend directly on provider-specific SDK details where a reasonable abstraction can isolate them.

Not every task requires an LLM.

Prefer deterministic software for tasks that can be reliably implemented without generative reasoning.

---

## 9. Research Behaviour

Research agents must distinguish:

* discovered evidence;
* interpretation of evidence;
* hypotheses;
* unresolved uncertainty.

A research agent must not fabricate:

* papers;
* authors;
* publication venues;
* DOIs;
* datasets;
* experimental results;
* quotations;
* statistical findings.

A citation being real does not prove that it supports a claim.

Evidence relevance must be checked separately from bibliographic existence.

Absence of evidence from one search is not sufficient to establish a research gap.

---

## 10. Software Engineering Behaviour

When modifying code:

1. inspect the relevant implementation;
2. inspect relevant tests;
3. understand the current contract;
4. make the smallest coherent change;
5. execute applicable tests when execution is available;
6. report what was and was not verified.

Do not claim code is working merely because it appears correct.

Use explicit language such as:

* `VERIFIED BY TEST`
* `NOT EXECUTED`
* `PARTIALLY VERIFIED`

when relevant.

---

## 11. Agent Permissions

Agents should operate with the minimum authority necessary for their task.

An agent should not automatically gain access to:

* every repository component;
* every external tool;
* unrestricted internet access;
* unrestricted filesystem access;
* arbitrary code execution;
* the ability to spawn unlimited sub-agents.

Permissions should be scoped according to role and task.

---

## 12. Bounded Execution

No autonomous workflow may rely on an unbounded loop.

Research, review, correction, retry, and sub-agent spawning must eventually be constrained by explicit execution budgets.

Relevant limits may include:

* iterations;
* model calls;
* token usage;
* searches;
* retries;
* parallel workers;
* wall-clock execution.

Repeated attempts that produce negligible new information should terminate.

Valid terminal states include:

* `COMPLETED`
* `FAILED`
* `UNKNOWN`
* `CONTESTED`
* `BLOCKED`
* `HUMAN_REVIEW_REQUIRED`
* `BUDGET_EXHAUSTED`

Agents must not manufacture certainty merely to avoid an unresolved terminal state.

---

## 13. Failure Learning

When a meaningful new failure mode is discovered, do not only fix the immediate instance.

Consider whether it should produce one or more of:

* a regression test;
* an evaluation case;
* a validation rule;
* a documented invariant;
* a failure taxonomy entry;
* an architectural change.

Prefer:

**failure discovered → classified → safeguard implemented → regression protection added**

when the cost is justified.

---

## 14. Human Escalation

Escalate rather than repeatedly retry when:

* evidence remains insufficient;
* an architectural decision is required;
* agents disagree without a reliable resolution mechanism;
* execution repeatedly fails for the same reason;
* the remaining decision is subjective or academic rather than technical;
* the execution budget is being consumed without meaningful progress;
* university or ethical requirements are unclear;
* a consequential research decision requires human ownership.

The human project owner has final authority over major research and project decisions.

---

## 15. Output Discipline

Agent outputs should clearly separate:

* facts;
* assumptions;
* proposed decisions;
* unresolved questions;
* verification results.

Avoid confident prose when confidence is not supported by evidence.

Do not hide uncertainty in verbose explanations.

Prefer structured artifacts when the output will be consumed by another agent or automated system.

---

## 16. Git and Change Review

The default development workflow is:

**branch → commit → pull request → human review → merge**

Agents must not assume permission to merge their own changes.

Changes to canonical project documents should be reviewable like source-code changes.

Where possible, commits should remain logically coherent and understandable independently.

Every pull request targeting `main` must include an update to
`CURRENT_STATE.md` that reflects the resulting repository state.

A pull request that does not modify `CURRENT_STATE.md` must fail the
repository's required Current State Gate and must not be merged.

---

## 17. Completion Criteria

An agent task is not complete merely because output was generated.

Before declaring completion, determine:

1. Was the requested artifact actually produced?
2. Was the relevant verification performed?
3. Are unresolved assumptions identified?
4. Were execution limits respected?
5. Were consequential changes surfaced for human review?
6. Does the resulting repository state remain consistent with canonical project documents?

If verification could not be performed, say so explicitly.
