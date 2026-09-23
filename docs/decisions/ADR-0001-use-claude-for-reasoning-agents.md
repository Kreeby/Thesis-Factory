# ADR-0001: Use Claude for Autonomous Reasoning Agents

Status: ACCEPTED
Date: 2026-09-23

## Context

Thesis Factory will contain autonomous AI agents responsible for tasks that require non-deterministic reasoning, such as:

* research planning;
* literature analysis;
* research criticism;
* experiment design;
* software-engineering reasoning;
* academic drafting;
* methodological review;
* claim and argument auditing.

The project requires a default LLM family for these reasoning workloads.

At the same time, the system should avoid coupling its domain logic and orchestration logic directly to one provider-specific API.

The project owner has explicitly selected Claude as the preferred LLM family for autonomous agents.

## Decision

Claude models accessed through the Anthropic API will be the required default LLM family for autonomous reasoning agents in Thesis Factory.

The exact Claude model is not fixed by this ADR.

Different agent roles may eventually use different Claude models or configurations when justified by quality, latency, context-window, or cost requirements.

Model access must be isolated behind a project-controlled interface or provider boundary where reasonably practical.

Domain logic, workflow state, and agent contracts should not directly depend on Anthropic-specific request or response structures.

This decision applies to generative reasoning agents.

It does not require non-generative AI components, embedding systems, parsers, search infrastructure, databases, validators, or deterministic tools to use Anthropic technology.

## Alternatives Considered

### Direct Anthropic integration throughout the codebase

Each agent could call the Anthropic API or SDK directly.

This was rejected as the architectural default because it would spread provider-specific concerns throughout agent and domain code, making testing, configuration, and future controlled comparisons harder.

### Provider-neutral system with no preferred model family

The project could treat all LLM providers as equally supported from the beginning.

This was not selected because the project currently has a clear operational preference for Claude, and implementing multi-provider parity before a concrete requirement exists would add unnecessary complexity.

### Other LLM families as the primary agent model

Other model providers may be technically capable of supporting the required workloads.

They were not selected as the project's default because the project owner has explicitly chosen Claude for autonomous reasoning agents.

This ADR does not prohibit future comparative evaluation.

## Consequences

### Positive

* Agent development has a clear default LLM target.
* Prompting and evaluation can initially focus on one model family.
* Model-provider concerns can remain isolated from domain logic.
* The architecture retains the ability to introduce alternative implementations later.
* Testing can substitute mock or deterministic model implementations behind the provider boundary.

### Negative

* The system will depend operationally on Anthropic API availability for autonomous reasoning workloads.
* Model behaviour, pricing, limits, and API changes may affect the system.
* Provider abstraction introduces a small amount of architectural overhead.
* Full portability to another provider is not guaranteed merely because an abstraction exists.

## Explicit Non-Decisions

This ADR does not decide:

* the exact Claude model to use;
* whether all agents use the same model;
* token or cost budgets;
* model-routing strategy;
* retry strategy;
* prompt-management framework;
* orchestration framework;
* Anthropic SDK version;
* embedding model;
* evaluation model;
* whether other models may be used for controlled experiments.

These decisions remain unresolved until concrete requirements justify them.

## Verification / Revisit Conditions

This decision should be reconsidered if one or more of the following occurs:

* Claude cannot satisfy a required agent capability;
* Anthropic API constraints materially prevent the intended architecture;
* cost or latency becomes unacceptable for the required workloads;
* evaluation demonstrates materially better results from another model family for a critical workload;
* university, legal, privacy, or data-governance requirements make the selected provider unsuitable;
* the project deliberately moves to a multi-provider model strategy.

Any change to the default reasoning-model family should supersede this ADR rather than silently modifying its historical decision.
