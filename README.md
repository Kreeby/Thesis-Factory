# Thesis Factory

Thesis Factory is an auditable AI-assisted research and software-engineering system for producing a master's thesis in Computer Science with a FinTech focus.

The project is not intended to generate a thesis from a single prompt. Its goal is to build a reproducible workflow in which research, evidence, software, experiments, academic claims, and human approvals remain traceable and reviewable.

## Project Status

**Phase 1 — Topic Researchability**

The project foundation is complete.

The current focus is implementing the first executable research workflow for evaluating whether candidate FinTech thesis topics are genuinely researchable.

The current implementation already supports scholarly discovery through OpenAlex, independent DOI metadata lookup through Crossref, normalized source artifacts, bibliographic comparison, source identity verification, and abstract ingestion.

## Current Direction

The next implementation step is the first Claude-backed reasoning component: structured scholarly-source relevance assessment.

No orchestration framework, database, vector store, or deployment architecture has been selected yet. These decisions remain requirement-driven.

## Documentation

* [`PROJECT.md`](PROJECT.md) — project goals, constraints, principles, and success criteria.
* [`ARCHITECTURE.md`](ARCHITECTURE.md) — current conceptual architecture.
* [`AGENTS.md`](AGENTS.md) — operating contract for AI agents working with the repository.
* [`CURRENT_STATE.md`](CURRENT_STATE.md) — current milestone, decisions, risks, and next actions.
* [`docs/decisions/`](docs/decisions) — Architecture Decision Records.

## Development Workflow

Changes normally follow:

**branch → commit → pull request → human review → merge**

The repository is the canonical source of project truth.

## Current Direction

The next major phase will define the first executable workflow for evaluating whether candidate FinTech thesis topics are genuinely researchable.

No orchestration framework, database, retrieval system, or application framework has been selected yet.
