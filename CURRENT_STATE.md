# Current Project State

Last updated: 2026-09-23

## Current Phase

**Phase 0 — Project Foundation**

The project is currently establishing its canonical documentation, decision process, and operating model before implementation begins.

---

## Current Objective

Complete the minimum project foundation required before designing or implementing the first research workflow.

---

## Completed

* GitHub repository created.
* `main` branch initialised.
* `project-foundation` development branch created.
* `PROJECT.md` created.
* `AGENTS.md` created.
* Claude selected as the required default LLM family for autonomous reasoning agents.
* Repository established as the canonical source of project truth.
* Branch → pull request → human review → merge established as the default development workflow.
* `ARCHITECTURE.md` created.
* ADR process established under `docs/decisions/`.
* ADR-0001 accepted: Claude selected as the default LLM family for autonomous reasoning agents.
---

## In Progress

Foundation pull request review.

No additional foundation artifacts are currently required.
---

## Not Started

The following work has intentionally not started yet:

* thesis topic selection;
* literature discovery;
* research-gap analysis;
* dataset selection;
* experiment design;
* application implementation;
* agent implementation;
* orchestration framework selection;
* persistence technology selection;
* retrieval architecture;
* evaluation framework implementation;
* thesis writing.

---

## Active Decisions

### Confirmed

* Autonomous reasoning agents will use Claude models through the Anthropic API by default.
* The system should remain architecturally isolated from provider-specific APIs where practical.
* LLM output is not treated as factual evidence.
* Agent execution must be bounded.
* Important project state must be externalised into repository artifacts.
* Human approval is required for consequential research decisions.
* Direct development changes should normally flow through pull requests.

### Not Yet Decided

* thesis topic;
* orchestration framework;
* model version or model-routing strategy;
* persistence technology;
* vector or retrieval technology;
* API framework;
* execution sandbox;
* experiment tracking system;
* observability stack;
* deployment architecture;
* final agent topology.

---

## Current Risks

### RISK-001 — Premature architecture

The project may adopt frameworks or infrastructure before concrete requirements justify them.

**Mitigation:** keep technology choices unresolved until driven by an actual workflow requirement.

### RISK-002 — Model-generated false certainty

LLMs may present unsupported or fabricated information with high confidence.

**Mitigation:** preserve epistemic state and require external verification for claims that can be checked.

### RISK-003 — Unbounded agent cost

Autonomous research or review loops may consume excessive model calls and tokens without meaningful progress.

**Mitigation:** require bounded execution and human escalation for non-converging workflows.

### RISK-004 — Documentation drift

Canonical documentation may accumulate speculative or contradictory rules over time.

**Mitigation:** `PROJECT.md` and root `AGENTS.md` are considered foundation documents and should only change for justified project-level reasons.

---

## Known Unknowns

The authoritative list of major unresolved project questions is maintained in `PROJECT.md`.

Current high-priority unknowns are:

1. University thesis requirements.
2. University policy for AI-assisted academic work.
3. Final FinTech thesis topic.
4. Criteria for determining whether a proposed topic is sufficiently researchable.
5. Data availability for candidate research topics.

---

## Next Actions

1. Complete review of the foundation pull request.
2. Merge the approved project foundation into `main`.
3. Begin Phase 1: define the **Topic Researchability** workflow.
---

## Current Milestone Exit Criteria

Phase 0 is complete when:

* canonical project documents exist;
* the decision-recording mechanism exists;
* current project state can be reconstructed from the repository;
* foundational operating rules are reviewable;
* the foundation changes have passed human review and have been merged;
* the project is ready to design its first executable workflow.
