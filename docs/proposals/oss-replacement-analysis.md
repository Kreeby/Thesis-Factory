# Thesis Factory — Current State and Improvement Proposal

Decision-support note: what the pipeline does today, what should be replaced with open-source tooling, and what must stay custom.

## Current State

Tags: `[D]` deterministic, `[LLM]`, `[EMB]` embedding model. Design rule: PROJECT.md §5.5 "prefer deterministic software where possible" — only 2 of 18 steps call an LLM.

```
TOPIC
  │
  1. Search planning ............ [LLM]  Claude → ≤5 bounded queries; topic treated as data, not instructions
  │
  2. Scholarly discovery ........ [D]    OpenAlex HTTP search; abstract rebuilt from inverted index
  3. Deduplication .............. [D]    merge by DOI, else provider+id
  │
  4. DOI cross-lookup ........... [D]    same DOI fetched independently from Crossref AND DataCite
  5. Bibliographic comparison ... [D]    DOI/title/year/authors → MATCH | MISMATCH | UNKNOWN per field
  6. Identity verification ...... [D]    fixed rule → CONFIRMED | CONFLICTING | INSUFFICIENT_DATA (no model call)
  │
  7. Relevance assessment ....... [LLM]  RELEVANT | NOT_RELEVANT | UNCERTAIN | INSUFFICIENT_EVIDENCE,
  │                                      grounded only in supplied abstract; no abstract → deterministic fallback
  8. Literature aggregation ..... [D]    bundles plan + verified + assessed sources
  9. Researchability decision ... [D]    per-dimension enum scoring (fit/lit/dataset/baselines/metrics/
  │                                      feasibility/contribution) → PASS | CONCERNS | FAIL | UNKNOWN
 10. University-fit check ....... [D]    rules vs pinned config/requirements/elte_ik_msc.json (ELTE IK guide)
```

Document / evidence pipeline — built, not yet wired to the above (CURRENT_STATE.md):

```
 11. Artifact fetching .......... [D]    HTTP download of PDFs/artifacts → immutable storage
 12. GROBID normalization ....... [D]    GROBID service → structured Document (ML model, fixed external tool)
 13. BM25 retrieval ............. [D]    lexical ranking over paragraph corpus
 14. Semantic retrieval ......... [EMB]  Voyage embeddings + cosine similarity
 15. Hybrid RRF fusion .......... [D]    reciprocal rank fusion of 13 + 14
 16. Retrieval evaluation ....... [D]    MRR/coverage vs frozen dev + held-out sets;
 │                                      voyage-4 standalone beat BM25 and RRF → RRF kept as documented negative result
 17. Evidence span addressing ... [D]    exact character-offset identity for a retrieved passage
 18. Evidence-span verification . NOT BUILT — next milestone (CURRENT_STATE.md):
                                         retrieval → context expansion → span proposal → deterministic
                                         verification → structured evidence artifact
```

## Proposed Improvements

```
  1. Search planning ............ [LLM]  KEEP — prompt-injection-guarded planner is project-specific
  2. Scholarly discovery ........ [D]    REPLACE → oksure/openalex-research-mcp (superset: 31 tools,
  │                                      citation networks, FT50/UTD24 presets, caching/retry, MCP or Skill)
  3. Deduplication .............. [D]    KEEP — trivial, and dedupe key is tied to internal source model
  4. DOI cross-lookup ........... [D]    FORK/EXTEND → citegate (add DataCite to its Crossref+OpenAlex path)
  5. Bibliographic comparison ... [D]    FORK/EXTEND → citegate field-by-field comparison logic
  6. Identity verification ...... [D]    KEEP verdict semantics — no tool does independent-registry
  │                                      CONFIRMED/CONFLICTING/INSUFFICIENT_DATA; refchecker does consensus voting
  7. Relevance assessment ....... [LLM]  FORK/EXTEND → extract AISysRev prompt + per-criterion schema pattern;
  │                                      keep the 4-state enum (AISysRev emits binary/ordinal/probability)
  8. Literature aggregation ..... [D]    KEEP — internal artifact assembly
  9. Researchability decision ... [D]    KEEP — no equivalent exists; thesis-scoping logic is the contribution
 10. University-fit check ....... [D]    KEEP — pinned ELTE IK requirements file, inherently local
 11. Artifact fetching .......... [D]    KEEP — immutable-storage contract is project-specific
 12. GROBID normalization ....... [D]    FORK/EXTEND → grobid_client_python for HTTP plumbing only;
  │                                      keep custom GROBID→Document mapping
 13. BM25 retrieval ............. [D]    REPLACE → pyserini BM25
 14. Semantic retrieval ......... [EMB]  KEEP Voyage (won the frozen benchmark); dense side may route via pyserini
 15. Hybrid RRF fusion .......... [D]    REPLACE → pyserini RRF (reference implementation, benchmarked)
 16. Retrieval evaluation ....... [D]    KEEP frozen dev/held-out sets; pyserini supplies MRR-style tooling
 17. Evidence span addressing ... [D]    KEEP — no tool does exact char-offset addressing bound to a
  │                                      normalized document version; genuine differentiator
 18. Evidence-span verification . [D]    BUILD CUSTOM — deterministic verification of proposed spans
      Governance layer ..........        KEEP — epistemic states (VERIFIED/DERIVED/ASSUMPTION/UNKNOWN),
                                         bounded budgets, human gates, staged provenance (ARCHITECTURE.md)
```

Stated plainly, not hedged: **most of this pipeline has no adequate open-source replacement.** Only 3 of 18 steps can be swapped wholesale (2, 13, 15). The steps that stay custom — independent-registry identity verification, exact-span evidence addressing, thesis researchability scoring, and the epistemic/budget/gate governance model — stay custom because nothing mature exists, not because of preference. That absence is the project's contribution surface.

## Position Replacements

- Scholarly discovery (step 2): custom thin OpenAlex HTTP client → oksure/openalex-research-mcp (https://github.com/oksure/openalex-research-mcp)
- DOI cross-lookup (step 4): hand-rolled Crossref + DataCite fetchers → fork chrisyangsong/citegate, add DataCite (https://github.com/chrisyangsong/citegate)
- Bibliographic comparison (step 5): custom field matcher → citegate field-comparison logic (https://github.com/chrisyangsong/citegate)
- Relevance assessment (step 7): custom Claude prompt + schema → AISysRev screening prompt/schema pattern, ported (https://github.com/EvoTestOps/AISysRev)
- GROBID plumbing (step 12): hand-rolled GROBID HTTP calls → grobid_client_python (https://github.com/kermitt2/grobid_client_python)
- BM25 retrieval (step 13): hand-rolled lexical ranker → pyserini BM25 (https://github.com/castorini/pyserini)
- Hybrid RRF fusion (step 15): hand-rolled RRF math → pyserini hybrid/RRF (https://github.com/castorini/pyserini)

Considered and rejected as wholesale replacements: markrussinovich/refchecker (consensus voting, no DataCite), DSL4-Digital/RefExists (2★, unaudited), future-house/paper-qa (no GROBID, embedding-only "hybrid", chunk/page citations not char spans), Stanford STORM (dormant, one-shot), SakanaAI/AI-Scientist (autonomous by design, opposite of gated).

## Comparison Table

| Area | Current (custom) | Proposed | Why Proposed Is Better | Reference |
|---|---|---|---|---|
| Scholarly discovery | Thin OpenAlex HTTP client, title/authors/DOI/abstract only (step 2) | oksure/openalex-research-mcp | Strict superset: 31 tools, citation networks, journal-quality presets, caching/retry, actively maintained, ships as MCP server or Skill. No reason to maintain a narrower version. | https://github.com/oksure/openalex-research-mcp |
| Reference verification internals | Hand-rolled Crossref+DataCite fetch and field matcher (steps 4-5) | Fork citegate, add DataCite | citegate already implements explicit verdict enums (verified/not-found/retracted/mismatch/unverifiable/error) and field-by-field registry comparison — 102★ of shared maintenance instead of solo-maintained matching code. Verdict semantics from ARCHITECTURE.md stay ours. | https://github.com/chrisyangsong/citegate |
| Abstract screening | Custom Claude prompt + 4-state enum (step 7) | Port AISysRev prompt/schema pattern | Closest architectural match: inclusion/exclusion criteria screening, pluggable LLMs, structured per-criterion scoring, actively maintained. Extract the pattern, not the app (it is a web app, not a library) — and keep the 4-state enum PROJECT.md requires. | https://github.com/EvoTestOps/AISysRev |
| Lexical + hybrid retrieval | Hand-rolled BM25 and RRF (steps 13, 15) | pyserini | Reference IR implementation for BM25 + dense + RRF with MRR-style benchmarking, 2,166★, active. Removes custom ranking math from the audit surface; the frozen benchmark from CURRENT_STATE.md can re-validate the swap and the RRF negative result. | https://github.com/castorini/pyserini |
| GROBID invocation | Hand-rolled GROBID HTTP plumbing (step 12) | grobid_client_python | Official client, 416★, handles batching/retries/timeouts. Replaces plumbing only; GROBID→Document normalization stays custom. | https://github.com/kermitt2/grobid_client_python |
| Identity-verification semantics | Independent-registry CONFIRMED / CONFLICTING / INSUFFICIENT_DATA (step 6) | KEEP CUSTOM — no adequate replacement | refchecker (517★) is the mature option but does multi-source consensus voting and has no DataCite; RefExists names the right registry pair but is 2★ and unaudited. Consensus voting cannot express "two independent registries disagree", which is the audit claim ARCHITECTURE.md needs. | https://github.com/markrussinovich/refchecker |
| Exact-span evidence provenance | Character-offset addressing tied to a normalized document version (steps 17-18) | KEEP CUSTOM — no match found | PaperQA2 (9,241★) resolves citations to chunk/page, not character spans. Nothing found addresses spans against a specific document version, which is the precondition for deterministic evidence verification in CURRENT_STATE.md. | https://github.com/future-house/paper-qa |
| Governance model | Epistemic states, bounded budgets, human gates, staged artifact provenance | KEEP CUSTOM — no match found | ARA-Labs/Agent-Native-Research-Artifact (682★) is the closest structurally but is a general ML lab-notebook format with no budget concept; verity (0★) is philosophically close but unproven with no epistemic vocabulary; STORM and AI-Scientist are dormant and ungated. No project combines staged provenance + epistemic tagging + hard iteration budgets + human gates. | https://github.com/ARA-Labs/Agent-Native-Research-Artifact |
