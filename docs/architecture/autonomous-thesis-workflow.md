# Autonomous Thesis Workflow — Target Architecture

Status: TARGET / NOT YET IMPLEMENTED
Working topic: **A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring**

## End product

The system is intended to support **one human-initiated, unattended, bounded run** (potentially about ten hours) producing a substantive MSc thesis draft **and traceable supporting research/experimental artifacts**, not merely a plausible text generator. A final academic submission is a human decision. No agent may invent source support, legal conclusions, experimental results, or claim university policy approval.

The full one-command ten-hour workflow is **not implemented by the October 2026 research-checkpoint PR**. Existing code covers important literature, retrieval, evidence, proposal-research, critic and writing building blocks; this change provides a shared logging and checkpoint substrate.

## Target stages (dependency-ordered, not independent generators)

| Stage | Output | Required gate |
|---|---|---|
| 0. Bootstrap | repo SHA, approved topic, configuration, budgets, environment preflight | human topic approval already recorded |
| 1. Research plan | bounded research questions and evidence requirements | schema, scope, budget |
| 2. Discovery | source and dataset candidates | discovery is **not** evidence |
| 3. Evidence verification | source identities, artifact hashes, exact spans | verified quotations / explicit unknown |
| 4. Researchability | multi-dimensional assessment, competing literature, research gap candidates | no fabricated novelty; human review if uncertain |
| 5. Study design | chosen datasets, licensed use, models, XAI methods, metrics, splits, pre-registered comparisons | method and feasibility approval |
| 6. Software & experiments | versioned code, tests, frozen data pointers, reproducible runs | tests, metrics, provenance and no data leakage |
| 7. Analysis | tables, figures, statistical outputs, uncertainty | results derived from actual experiment artifacts |
| 8. Thesis drafting | structured chapters, references, claim-to-evidence map | citation/claim validation and academic policy |
| 9. Independent audit | adversarial critique, reproducibility review | fail/unknown/human review are valid terminal states |
| 10. Final package | thesis document and reproducibility package | human acceptance before submission |

## Unattended execution requirements (future work)

A long-lived orchestrator must own **total** wall-clock, per-provider budgets, maximum retries, concurrency, explicit terminal states, resumability, dependency DAG and human gates. It must halt or preserve `UNKNOWN` when evidence is insufficient. A ten-hour clock does not authorize fabricated completeness. Agents may work unattended within granted policies, but must pause at decisions requiring human approval.

Current run wrapper only bounds **one subprocess stage** (up to ten hours), captures append-only structured events, locally writes stdout/stderr, and allows controlled rerun attempts. It does **not** implement the full DAG, cross-stage budget accounting, provider tracing, a remote work queue or automatic human decisions.

## Intermediate Pull Requests

Intermediate PRs are **review artifacts**, not automatic approval:

1. A stage or group of stages completes with explicit status and local evidence checkpoint.
2. Code changes are committed on a dedicated branch by a separately authorized actor.
3. A redacted PR body is generated from run status metadata.
4. An actor explicitly opens the PR (`gh pr create`) after pushing and reviewing the diff. No automatic merge.
5. Unreviewed or failed stages remain visible, with human escalation as appropriate.

The `prepare_intermediate_pr.py` helper implements steps 3–4 only. This is deliberately distinct from implementing remote Git writes or a merge agent.

## Trust and provenance

```
source bytes → SHA-256 → normalized paragraph → exact span
                                         ↓
                                      research finding
                                         ↓
                               study design / experiment
                                         ↓
                              measured result → thesis claim
```

- Domain validation is not semantic entailment verification.
- Journal metadata does not store arbitrary output text or secrets.
- Original research JSON bytes are stored by SHA-256 under local ignored `.thesis-runs/` (not pushed by default).
- The PR body contains stage status and counts only, not raw papers, citations, prompts, raw logs or evidence.
- Auditability requires linking dataset/code/config versions to any **future** experiments.
- The current external Project Proposal draft is a historical, deadline-specific artifact, not evidence of a successful Critic PASS-gated run.

## Exit criterion for the first implementation slice

- Given already collected JSON, one offline command validates schema and task/topic identity and stores immutable local copies.
- Any existing CLI can be run with stage-level outcome, git SHA, stdout/stderr and a timeout recorded locally.
- A draft intermediate PR description is generated without leaking research data and without merging.
- Tests are local and do not call Anthropic, Voyage, OpenAlex or GitHub.
- `CURRENT_STATE.md` is updated with truthful incremental status.
