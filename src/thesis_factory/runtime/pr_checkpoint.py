"""Prepare a sanitized intermediary PR description from a local run journal.

Never publish raw logs or research JSON in a PR body.
"""

from __future__ import annotations

from pathlib import Path

from thesis_factory.runtime.journal import (
    append_event, create_run_directory, read_events,
)

_STAGE_EVENTS = frozenset({"STAGE_STARTED", "STAGE_COMPLETED", "STAGE_FAILED", "STAGE_TIMED_OUT"})


def prepare_pr_body(*, root: Path, run_id: str, title: str,
                    stage: str, git_sha: str) -> tuple[Path, bool]:
    run_dir = create_run_directory(root, run_id)
    events = read_events(run_dir, run_id=run_id)
    latest: dict[str, dict] = {}
    for event in events:
        if event["event_type"] in _STAGE_EVENTS:
            latest[event["stage"]] = event
    # No log contents, URL, command arguments, dataset records, citations or
    # model prompts enter this publicly reviewable PR body.
    checkpoints = [e for e in events if e["event_type"] == "CHECKPOINT_CREATED"]
    failures = [e for e in latest.values() if e["event_type"] != "STAGE_COMPLETED"]
    if not latest and not checkpoints:
        raise ValueError("no completed stages or checkpoints recorded")
    lines = [f"## {title}", "", "Intermediate, human-reviewable checkpoint.", "",
             f"- Run ID: `{run_id}`", f"- Git SHA: `{git_sha}`",
             f"- Requested checkpoint: `{stage}`", "",
             "### Stage outcomes", ""]
    for name, event in sorted(latest.items()):
        metadata = event["metadata"]
        lines.append(f"- `{name}`: **{event['event_type']}**, "
                     f"exit={metadata.get('exit_code', 'n/a')}")
    lines += ["", "### Research snapshots", "",
              f"- Local content-addressed checkpoints recorded: **{len(checkpoints)}**",
              "- Raw evidence and stdout/stderr remain local and are not attached.", "",
              "### Review gate", "",
              "- [ ] Human review of sources, claims, tests and scope",
              "- [ ] Confirm no secrets or raw artifacts are in the Git diff",
              "- [ ] Do not merge automatically", ""]
    if failures:
        lines.extend(["**Attention:** at least one stage is incomplete, failed, or timed out.", ""])
    body_file = run_dir / f"intermediate-pr-{stage}.md"
    body_file.write_text("\n".join(lines), encoding="utf-8")
    body_file.chmod(0o600)
    append_event(run_dir, run_id, stage, "PR_PREPARED", metadata={
        "failed_stages": len(failures), "checkpoints": len(checkpoints),
    })
    return body_file, not failures
