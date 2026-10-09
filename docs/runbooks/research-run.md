# Runbook: stage logging and research checkpoints

This is a **local, provider-free infrastructure slice**, not a complete thesis-generation command.

## 1. Create a work branch

```sh
git checkout main
git pull --ff-only
git switch -c phase1/research-checkpoint-logging
```

`git apply` the associated patch from the repository root before running these commands.

## 2. Log an existing stage

```sh
./scripts/uv run python scripts/run_logged_stage.py \
  --run-id credit-xai-001 --stage local_tests --timeout-sec 600 \
  -- ./scripts/uv run pytest
```

Repeat with other existing scripts as appropriate. Provider-backed scripts may incur cost; `run_logged_stage.py` does **not** silently invoke them. Each stage execution appends `STAGE_STARTED` plus a terminal event to `.thesis-runs/<run_id>/events.jsonl`. Logs are written incrementally to `.thesis-runs/<run_id>/steps/<stage>-<attempt>/stdout.log` and `stderr.log`.

Use `tail -f .thesis-runs/credit-xai-001/steps/local_tests-0001/stdout.log` to follow long stages. A per-stage timeout kills its subprocess process group. A whole-run budget/orchestrator has **not** been implemented.

**Security:** logs may contain model responses, source materials or credentials printed by third-party tools. The run directory is ignored by Git and local file permissions are restricted. Never attach raw logs to PRs or publish them without inspecting/redacting them.

## 3. Preserve already collected research artifacts

Example (adjust directory/file names; select the actual final `v3` primary evidence, not an earlier short checkpoint):

```sh
./scripts/uv run python scripts/checkpoint_research.py \
  --run-id credit-xai-001 \
  --artifact discovery=../Thesis-Factory-research-artifacts/proposal_discovery.json \
  --artifact verification_plan=../Thesis-Factory-research-artifacts/proposal_verification_plan.json \
  --artifact scholarly_evidence=../Thesis-Factory-research-artifacts/proposal_scholarly_evidence_v2.json \
  --artifact primary_evidence=../Thesis-Factory-research-artifacts/proposal_primary_evidence_v3.json \
  --artifact research_draft=../Thesis-Factory-research-artifacts/proposal_research_draft.json \
  --artifact document_draft=../Thesis-Factory-research-artifacts/proposal_document_draft.json
```

An incomplete set of artifacts can also be checkpointed; unknown stages remain unknown and research/evidence linkage is explicitly `DEFERRED` until all planned evidence-task results are present. `CHECKPOINT_CREATED` means **local schema and identity validation**, not a fresh check against external source bytes or semantic entailment of a claim.

The original bytes are saved as `<sha256>.json` under `.thesis-runs/<run-id>/artifacts/`. An immutable numbered manifest is saved in `checkpoints/`. Future snapshots append; they do not overwrite prior snapshots.

If any artifact schema is stale or conflicting, the command fails without creating a checkpoint. Investigate the file/version mismatch; do not weaken Pydantic contracts to make the pipeline pass.

## 4. Prepare an intermediate PR

With a pushed feature branch and successful stages:

```sh
./scripts/uv run python scripts/prepare_intermediate_pr.py \
  --run-id credit-xai-001 --stage research_checkpoint \
  --title "Phase 1: research checkpoint and durable run journal"
```

This is a **dry run** and writes a local body file. To actually create the PR after reviewing the diff:

```sh
./scripts/uv run python scripts/prepare_intermediate_pr.py \
  --run-id credit-xai-001 --stage research_checkpoint \
  --title "Phase 1: research checkpoint and durable run journal" --create
```

Requires GitHub CLI (`gh`), authentication, a pushed branch and clean working tree. The helper does not stage/commit/push/merge, and rejects opening a PR when a stage failed or timed out. Check the code diff for secrets before invoking `--create`.

## 5. Smoke tests

```sh
./scripts/uv run pytest tests/runtime -q
./scripts/uv run pytest
```

These tests are local and do not call paid research providers. For real research calls, configure budgets and credentials explicitly and use the logged wrapper.

## Future ten-hour one-run operation

A one-command orchestrator that sequences discovery → evidence → researchability → experiments → analysis → chapters → critique with **global** cost/time limits and intermediate PR automation is future work. The current slice only establishes safe local logging and checkpoints needed to make that possible.
