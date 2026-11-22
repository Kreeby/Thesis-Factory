# ADR-0003: Local Models Inside Code, Claude Code as Orchestrating Agent

Status: ACCEPTED (owner approved PR #18, 2026-11-16)
Date: 2026-11-16
Supersedes (when accepted): ADR-0001 in the part "accessed through the Anthropic API"

## Context

The project owner has a regular Claude subscription and a ChatGPT Plus subscription, basic (free) Voyage and OpenAlex access, an Apple M4 Mac with 16 GB RAM, and abundant wall-clock time but scarce paid tokens. The research goal now requires reading at the scale of thousands to hundreds of thousands of papers, which is arithmetically impossible through paid per-token LLM calls (100k abstracts × ~300 tokens ≈ 30M tokens).

Repository code currently calls the Anthropic API directly (`AnthropicStructuredReasoner`) and Voyage for embeddings, so AI-written code pays for a second remote AI at runtime. The owner explicitly wants to remove that dependency for bulk work.

## Decision proposed for review

1. **Repository code does not call remote LLM providers by default.** Bulk structured tasks (relevance screening, quote-candidate proposal, field extraction, labelling) run on local models via Ollama behind the existing `StructuredReasoner` protocol (`OllamaStructuredReasoner`).
2. **Heavy reasoning** (critical appraisal synthesis, research-gap synthesis, study design, legal interpretation, thesis prose, audit) is performed by the orchestrating agent session (Claude Code on the owner's subscription; Codex CLI as an independent second reviewer/coder), operating on artifacts produced by the deterministic toolkit — not by code calling an API.
3. **Hallucination control is architectural, not model-dependent.** Every factual output of any model must pass a deterministic gate before acceptance: exact-span verification against SHA-256-identified text, DOI/registry identity checks, or linkage to a recorded experiment artifact. Outputs that fail become `NOT_SUPPORTED` / `UNKNOWN`, never prose.
4. **Switching a task to a local model requires an evaluation result**, not an assumption. Anthropic and Voyage clients remain in the codebase as disabled fallbacks until evaluations justify removal.
5. Truncated structured output is an explicit error for every provider (`stop_reason == "max_tokens"`, Ollama `done_reason == "length"`).

## Evidence at proposal time

Relevance eval (`evals/relevance/cases.json`, 7 cases, temperature 0, 2026-11-16, M4 16 GB):

| Model | Passed | Wall-clock (7 cases incl. load) |
|---|---|---|
| `qwen3:8b` (Ollama) | 6/7 | 23.8 s |
| `llama3.1:8b` (Ollama) | 5/7 | 18.8 s |

`qwen3:8b` failed `broad-financial-ml-review` (expected `UNCERTAIN`, got `NOT_RELEVANT`) — a false negative, which is the costly error for screening. Seven cases are **not statistically sufficient**; this table justifies further evaluation, not adoption. No Claude baseline was re-run (no API spend).

## Alternatives considered

- Keep Anthropic API for all reasoning: rejected for bulk work on cost grounds; retained as fallback.
- Local models for everything: rejected — 8–14B models fitting 16 GB are materially weaker at synthesis and academic writing, which would lower thesis quality.
- Creating additional provider accounts to multiply free tiers: rejected — violates provider terms.

## Consequences

Positive: bulk reading cost becomes local compute time; no secret keys needed for screening/extraction; runs can be resumed across subscription windows. Negative: local model quality must be evaluated per task; long runs depend on the Mac staying awake; subscription limits for headless agent sessions are not precisely documented and must be measured.

## Revisit conditions

A larger evaluation set shows local models below an agreed threshold for a task; a GPU server becomes available (larger local models); subscription terms for headless use change.
