# ADR-0002: Local Run Journal, Research Checkpoints, and Intermediate PR Reviews

Status: PROPOSED
Date: 2026-10-09

## Context

Thesis Factory intends eventually to run bounded, long-duration autonomous thesis research and experimentation. The first live proposal produced valuable verified artifacts, but run state, failed Critic output and the final DOCX were not reproducibly integrated into the repository. The user requests project-wide execution logging and intermediate pull requests.

## Decision proposed for review

Introduce a dependency-light local execution journal as the first provenance infrastructure slice:

- Versioned append-only JSONL events, with run ID, stage ID, event type, UTC timestamp and **allowlisted structured metadata**.
- Durable, private stdout/stderr files for existing CLI subprocesses, with per-stage timeout, exit code, attempts and Git SHA.
- Immutable SHA-256 copies and versioned checkpoint manifests for already-existing research JSON, after schema and cross-artifact identity checks.
- A local intermediate PR-body generator, with explicit `--create` through existing GitHub CLI; **never auto-merge**.
- No remote provider calls, external database, orchestration framework or automatic PR publishing as a side effect of checkpoint creation.

This implementation is approved only when the PR is reviewed and merged; the ADR is `PROPOSED` until then.

## Alternatives considered

- Embed logging separately in every Anthropic, OpenAlex, retrieval and research module: rejected for the first slice because it multiplies invasive changes and misses subprocess failures.
- Introduce Temporal/LangGraph/event database immediately: rejected until a tested, resumable DAG and cross-stage durability requirements justify such infrastructure.
- Commit raw logs and research data in every PR: rejected because of data size, source rights, sensitive outputs, secrets and unnecessary review noise.
- Generate PRs and merge them automatically during an unattended run: rejected because human authority and code review are explicit constraints.

## Consequences

Positive: low-cost workflow observability now; stable run IDs; local artifact preservation; auditable intermediate review boundaries. Negative: private local files require backup; JSONL does not provide distributed concurrency guarantees; the wrapper alone does not track Anthropic/Voyage token usage; human-review gates prevent genuinely unconditional 10-hour end-to-end submission.

## Revisit conditions

Revisit once multi-process/concurrent execution, crash recovery, remote artifact storage, dataset compliance, provider billing telemetry or an orchestrator with total-run limits becomes a concrete tested need. Add a superseding ADR for a durable orchestration/persistence decision; do not silently make the wrapper a production scheduler.
