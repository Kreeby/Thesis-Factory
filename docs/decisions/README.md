# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for Thesis Factory.

An ADR records a significant project decision together with the context in which it was made, the alternatives considered, and the consequences of the decision.

ADRs exist to prevent important architectural decisions from becoming implicit knowledge stored only in conversations, model memory, or individual developers' heads.

## When to create an ADR

Create an ADR when a decision has meaningful long-term consequences for the project and would be expensive, confusing, or risky to rediscover later.

Typical examples include decisions about:

* LLM providers and model strategy;
* orchestration architecture;
* persistence technology;
* retrieval architecture;
* provenance representation;
* agent isolation and permissions;
* execution sandboxing;
* evaluation strategy;
* observability;
* deployment architecture;
* major external integrations.

Not every implementation choice requires an ADR.

Local refactoring, routine dependency updates, naming decisions, and easily reversible implementation details should normally remain in code, tests, issues, or pull requests.

## Status

Each ADR has one of the following statuses:

* `PROPOSED` — under consideration;
* `ACCEPTED` — currently authoritative;
* `REJECTED` — considered but not adopted;
* `SUPERSEDED` — replaced by a later ADR;
* `DEPRECATED` — no longer applicable.

An accepted ADR remains authoritative until explicitly superseded or deprecated.

## Naming

Use sequential identifiers:

```text
ADR-0001-short-decision-title.md
ADR-0002-another-decision.md
```

Identifiers are never reused.

## ADR Structure

Each ADR should contain:

```text
# ADR-NNNN: Decision title

Status:
Date:

## Context

What problem or constraint requires a decision?

## Decision

What has been decided?

## Alternatives Considered

What realistic alternatives were considered?

## Consequences

What becomes easier, harder, possible, or constrained because of this decision?

## Verification / Revisit Conditions

How can we determine whether this decision remains appropriate?
Under what conditions should it be reconsidered?
```

The structure may be extended when a decision requires additional information, but unnecessary sections should not be added by default.

## Decision Discipline

An ADR should document a decision that has actually been made.

Do not create an accepted ADR merely because a technology has been discussed.

If the project has not yet made the decision, either:

* leave the question unresolved; or
* create a `PROPOSED` ADR when structured evaluation is useful.

Unknowns should remain unknown until sufficient information exists to resolve them.

## Relationship to Other Documents

`PROJECT.md` defines project-level goals, constraints, and principles.

`AGENTS.md` defines global operating rules for AI agents.

`ARCHITECTURE.md` describes the current architecture.

ADRs explain **why significant architectural decisions were made**.

`CURRENT_STATE.md` describes where the project currently stands.

When these artifacts conflict, the conflict should be resolved explicitly rather than silently interpreted by an agent.
