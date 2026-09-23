# Topic Researchability Architecture

**Status:** IN PROGRESS
**Phase:** 1 — Topic Researchability

This document distinguishes the architecture that is implemented today from the intended target architecture for Phase 1.

The diagrams describe logical responsibilities and data flow. They do not imply separate deployed services.

---

## 1. Current Implemented State

The current implementation discovers scholarly sources, normalizes provider data, verifies bibliographic identity using an independent registry, and reconstructs abstracts when OpenAlex provides them.

```mermaid
flowchart TD

    HUMAN["Human / test query"]

    HUMAN --> WORKFLOW["discover_and_verify_sources"]

    subgraph DISCOVERY["Scholarly Discovery"]
        OA_CLIENT["OpenAlexClient"]
        OA_API["OpenAlex API"]
        OA_ADAPTER["OpenAlex adapter"]
    end

    WORKFLOW --> OA_CLIENT
    OA_CLIENT --> OA_API
    OA_API -->|Raw JSON| OA_ADAPTER
    OA_ADAPTER --> SOURCE["SourceRecord"]

    SOURCE --> DOI_CHECK{"DOI available?"}

    DOI_CHECK -->|No| NO_DOI["NO_DOI"]
    DOI_CHECK -->|Yes| CR_CLIENT["CrossrefClient"]

    subgraph REGISTRY["Independent Bibliographic Registry"]
        CR_CLIENT
        CR_API["Crossref API"]
        CR_ADAPTER["Crossref adapter"]
    end

    CR_CLIENT --> CR_API
    CR_API -->|Raw JSON| CR_ADAPTER
    CR_ADAPTER --> REGISTRY_SOURCE["Registry SourceRecord"]

    SOURCE --> COMPARE["Bibliographic comparison"]
    REGISTRY_SOURCE --> COMPARE

    COMPARE --> DOI_MATCH["DOI comparison"]
    COMPARE --> TITLE_MATCH["Title comparison"]
    COMPARE --> YEAR_MATCH["Publication year comparison"]
    COMPARE --> AUTHOR_MATCH["Author comparison"]

    DOI_MATCH --> IDENTITY["Identity verification"]
    TITLE_MATCH --> IDENTITY
    YEAR_MATCH --> IDENTITY
    AUTHOR_MATCH --> IDENTITY

    IDENTITY --> CONFIRMED["CONFIRMED"]
    IDENTITY --> CONFLICTING["CONFLICTING"]
    IDENTITY --> INSUFFICIENT["INSUFFICIENT_DATA"]
```

### Abstract ingestion

OpenAlex may expose an abstract as an inverted index rather than ordinary text.

The OpenAlex adapter reconstructs that representation before it enters the rest of the system.

```mermaid
flowchart LR

    OPENALEX["OpenAlex API"]
    INVERTED["abstract_inverted_index"]
    ADAPTER["OpenAlex adapter"]
    ABSTRACT["Reconstructed abstract"]
    SOURCE["SourceRecord"]

    OPENALEX --> INVERTED
    INVERTED --> ADAPTER
    ADAPTER --> ABSTRACT
    ABSTRACT --> SOURCE
```

---

## 2. Current Trust Boundary

External provider data is not treated as trusted domain state merely because an API returned it.

```mermaid
flowchart LR

    INTERNET["External scholarly APIs"]
    RAW["Untrusted provider data"]
    ADAPTER["Provider-specific adapter"]
    DOMAIN["Validated SourceRecord"]
    VERIFY["Deterministic verification"]
    RESULT["Verification artifact"]

    INTERNET --> RAW
    RAW --> ADAPTER
    ADAPTER --> DOMAIN
    DOMAIN --> VERIFY
    VERIFY --> RESULT
```

The current pipeline therefore preserves the following distinctions:

```text
discovery != verification
verification != relevance
relevance != evidence
evidence != research conclusion
```

Bibliographic identity verification currently requires no LLM.

---

## 3. Current Implemented Components

```mermaid
flowchart TD

    subgraph DOMAIN["Domain"]
        SOURCE["SourceRecord"]
    end

    subgraph INTEGRATIONS["External Integrations"]
        OA["OpenAlexClient"]
        CR["CrossrefClient"]
    end

    subgraph VERIFICATION["Verification"]
        BC["BibliographicComparison"]
        IV["IdentityVerification"]
    end

    subgraph WORKFLOWS["Workflow"]
        DV["discover_and_verify_sources"]
    end

    OA --> SOURCE
    CR --> SOURCE

    DV --> OA
    DV --> CR

    SOURCE --> BC
    BC --> IV
```

At this stage:

* OpenAlex performs scholarly discovery.
* Crossref provides an independent DOI registry lookup.
* external metadata is normalized into `SourceRecord`;
* bibliographic fields are compared deterministically;
* identity is classified as `CONFIRMED`, `CONFLICTING`, or `INSUFFICIENT_DATA`;
* discrepancies remain visible rather than being silently discarded;
* abstracts are reconstructed when available;
* no reasoning agent has yet been added to this pipeline.

---

# 4. Phase 1 Target State

Phase 1 is not intended to generate thesis prose.

Its goal is to determine whether a proposed thesis topic is sufficiently researchable to justify deeper research and experimentation.

The desired workflow is:

```mermaid
flowchart TD

    HUMAN["Human proposes candidate thesis topic"]

    HUMAN --> ORCHESTRATOR["Topic Researchability Workflow"]

    subgraph PLANNING["Research Planning"]
        PLANNER["Research Planner<br/>Claude"]
        QUERIES["Search queries and research subquestions"]
    end

    ORCHESTRATOR --> PLANNER
    PLANNER --> QUERIES

    subgraph DISCOVERY["Literature Discovery"]
        OPENALEX["OpenAlex"]
        FUTURE_SOURCE["Additional scholarly provider<br/>only if justified"]
    end

    QUERIES --> OPENALEX
    QUERIES --> FUTURE_SOURCE

    OPENALEX --> DISCOVERED["Discovered SourceRecords"]
    FUTURE_SOURCE --> DISCOVERED

    subgraph VERIFY["Bibliographic Verification"]
        DOI_REGISTRY["Crossref"]
        BIB_COMPARE["Bibliographic comparison"]
        IDENTITY["Identity verification"]
    end

    DISCOVERED --> DOI_REGISTRY
    DISCOVERED --> BIB_COMPARE
    DOI_REGISTRY --> BIB_COMPARE
    BIB_COMPARE --> IDENTITY

    IDENTITY --> IDENTITY_GATE{"Identity confirmed?"}

    IDENTITY_GATE -->|No| REVIEW["Reject, flag, or request more evidence"]
    IDENTITY_GATE -->|Yes| ABSTRACT_GATE{"Abstract available?"}

    ABSTRACT_GATE -->|No| INSUFFICIENT_ABSTRACT["INSUFFICIENT_EVIDENCE"]
    ABSTRACT_GATE -->|Yes| RELEVANCE["Relevance Assessment<br/>Claude"]

    subgraph REASONING["Research Reasoning"]
        RELEVANCE
        EVIDENCE["Evidence extraction"]
        CRITIC["Adversarial Research Critic<br/>Claude"]
    end

    RELEVANCE --> RELEVANCE_GATE{"Relevant?"}

    RELEVANCE_GATE -->|No| EXCLUDE["Exclude from relevant evidence set"]
    RELEVANCE_GATE -->|Uncertain| REVIEW
    RELEVANCE_GATE -->|Yes| EVIDENCE

    EVIDENCE --> CRITIC

    subgraph ANALYSIS["Topic Researchability Analysis"]
        LITERATURE["Relevant literature exists?"]
        GAP["Plausible research gap?"]
        DATA["Usable data available?"]
        BASELINE["Baseline or comparator exists?"]
        METRICS["Measurable evaluation exists?"]
        FEASIBILITY["Experiment feasible?"]
        CONTRIBUTION["Master's-level contribution plausible?"]
    end

    CRITIC --> LITERATURE
    CRITIC --> GAP

    ORCHESTRATOR --> DATA
    ORCHESTRATOR --> BASELINE
    ORCHESTRATOR --> METRICS
    ORCHESTRATOR --> FEASIBILITY
    ORCHESTRATOR --> CONTRIBUTION

    LITERATURE --> REPORT["Structured Researchability Report"]
    GAP --> REPORT
    DATA --> REPORT
    BASELINE --> REPORT
    METRICS --> REPORT
    FEASIBILITY --> REPORT
    CONTRIBUTION --> REPORT

    REPORT --> HUMAN_GATE{"Human review"}

    HUMAN_GATE -->|Approve| ACCEPT["Candidate accepted for deeper research"]
    HUMAN_GATE -->|Reject| REJECT["Candidate rejected"]
    HUMAN_GATE -->|Insufficient evidence| UNKNOWN["UNKNOWN / more research required"]
```

---

## 5. Intended Reasoning Boundary

Claude should operate on verified or explicitly uncertain artifacts rather than unrestricted model memory.

```mermaid
flowchart LR

    VERIFIED["Verified project artifacts"]
    AGENT["Claude reasoning component"]
    STRUCTURED["Structured output"]
    VALIDATION["Schema and policy validation"]
    DOWNSTREAM["Downstream workflow"]

    VERIFIED --> AGENT
    AGENT --> STRUCTURED
    STRUCTURED --> VALIDATION
    VALIDATION --> DOWNSTREAM
```

The intended pattern is:

```text
LLM proposes
    ↓
structured artifact
    ↓
software validates
    ↓
evidence supports
    ↓
human approves when required
```

Claude-generated output is not evidence by itself.

---

## 6. Target Researchability Dimensions

A candidate topic should eventually be evaluated against several independent dimensions.

```mermaid
flowchart TD

    TOPIC["Candidate Topic"]

    TOPIC --> D1["Problem existence"]
    TOPIC --> D2["Relevant academic literature"]
    TOPIC --> D3["Plausible research gap"]
    TOPIC --> D4["Data availability"]
    TOPIC --> D5["Baseline or comparator"]
    TOPIC --> D6["Measurable evaluation"]
    TOPIC --> D7["Experiment feasibility"]
    TOPIC --> D8["Appropriate academic contribution"]

    D1 --> REPORT["Researchability Report"]
    D2 --> REPORT
    D3 --> REPORT
    D4 --> REPORT
    D5 --> REPORT
    D6 --> REPORT
    D7 --> REPORT
    D8 --> REPORT
```

A single positive signal must not automatically imply that a topic is researchable.

For example:

```text
many papers exist
```

does not by itself establish:

```text
a research gap exists
```

and:

```text
an interesting problem exists
```

does not by itself establish:

```text
usable data or a feasible experiment exists
```

---

## 7. Target Provenance

Every consequential researchability conclusion should eventually be traceable backwards.

```mermaid
flowchart RL

    DECISION["Human research decision"]
    REPORT["Researchability report"]
    CLAIM["Researchability claim"]
    EVIDENCE["Evidence record"]
    SOURCE["Verified scholarly source"]
    PROVIDER["Provider record"]

    DECISION --> REPORT
    REPORT --> CLAIM
    CLAIM --> EVIDENCE
    EVIDENCE --> SOURCE
    SOURCE --> PROVIDER
```

Example:

```text
Relevant academic literature exists
        ↓
researchability claim
        ↓
supporting evidence records
        ↓
verified scholarly sources
        ↓
OpenAlex and Crossref identifiers
```

The intended architecture is therefore not:

```text
topic
  ↓
Claude
  ↓
yes / no
```

It is:

```text
topic
  ↓
research planning
  ↓
literature discovery
  ↓
source verification
  ↓
relevance assessment
  ↓
evidence extraction
  ↓
adversarial review
  ↓
researchability analysis
  ↓
structured report
  ↓
human decision
```

---

## 8. Current vs Target

```mermaid
flowchart LR

    subgraph CURRENT["Current"]
        C1["Query"]
        C2["OpenAlex discovery"]
        C3["Source normalization"]
        C4["Crossref verification"]
        C5["Identity verification"]
        C6["Abstract ingestion"]

        C1 --> C2
        C2 --> C3
        C3 --> C4
        C4 --> C5
        C3 --> C6
    end

    subgraph TARGET["Phase 1 Target"]
        T1["Research planning"]
        T2["Verified literature"]
        T3["Relevance assessment"]
        T4["Evidence extraction"]
        T5["Adversarial criticism"]
        T6["Researchability dimensions"]
        T7["Researchability report"]
        T8["Human decision"]

        T1 --> T2
        T2 --> T3
        T3 --> T4
        T4 --> T5
        T5 --> T6
        T6 --> T7
        T7 --> T8
    end

    CURRENT --> TARGET
```

---

## 9. Explicit Non-Decisions

The Phase 1 target architecture does not currently select:

* an orchestration framework;
* LangGraph;
* a database;
* a vector database;
* a persistence implementation;
* MCP;
* a deployment architecture;
* a frontend framework;
* the final number of reasoning agents;
* the exact Claude model for every reasoning role;
* the final evidence persistence schema;
* the final evaluation framework.

These choices should be introduced only when an executable requirement justifies them.

---

## 10. Architecture Evolution Rule

The Phase 1 architecture should evolve according to:

```text
requirement
    ↓
minimal implementation
    ↓
execution
    ↓
observed behaviour
    ↓
failure or missing capability
    ↓
minimal architectural change
```

The target diagram is directional rather than a commitment to implement every box exactly as currently drawn.

The current implementation remains authoritative for what the system actually does today.
