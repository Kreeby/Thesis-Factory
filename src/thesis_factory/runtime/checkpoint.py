"""Offline checkpoint for the proposal research artifacts.

Schema validation and cross-artifact identity checks are deterministic, but
cannot prove that claims are entailed by citations or that remote source bytes
were retrieved correctly. Original JSON bytes are stored by SHA-256 locally.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from thesis_factory.runtime.journal import (
    append_event, create_run_directory, utc_now, write_json_atomically,
)

ROLES = (
    "discovery", "verification_plan", "scholarly_evidence",
    "primary_evidence", "research_draft", "document_draft",
)
MAX_ARTIFACT_BYTES = 30 * 1024 * 1024


class CheckpointError(ValueError):
    pass


def _parse_role(role: str, path: Path):
    # Lazy imports: stage journaling remains stdlib-only, no Anthropic calls.
    if role == "discovery":
        from thesis_factory.research.discovery_artifact import load_discovery_artifact
        return load_discovery_artifact(path)
    if role == "verification_plan":
        from thesis_factory.domain.proposal_verification import ProposalVerificationPlan
        model = ProposalVerificationPlan
    elif role == "scholarly_evidence":
        from thesis_factory.domain.scholarly_verification import ScholarlyVerificationRun
        model = ScholarlyVerificationRun
    elif role == "primary_evidence":
        from thesis_factory.domain.primary_source import PrimaryVerificationRun
        model = PrimaryVerificationRun
    elif role == "research_draft":
        from thesis_factory.domain.proposal_research import ProposalResearchDraft
        model = ProposalResearchDraft
    elif role == "document_draft":
        from thesis_factory.domain.proposal_research import ProposalDocumentDraft
        model = ProposalDocumentDraft
    else:
        raise CheckpointError("unrecognized artifact role")
    return model.model_validate_json(path.read_bytes())


def _check_linkage(parsed: dict[str, Any]) -> dict[str, Any]:
    topics = {
        getattr(value, "topic", getattr(value, "approved_topic", None))
        for value in parsed.values() if hasattr(value, "topic") or hasattr(value, "approved_topic")
    }
    if len(topics) > 1:
        raise CheckpointError("artifact topics disagree")
    plan = parsed.get("verification_plan")
    if plan is not None:
        by_id = {task.task_id: task for task in plan.tasks}
        for role in ("scholarly_evidence", "primary_evidence"):
            run = parsed.get(role)
            if run is None:
                continue
            for item in run.task_results:
                task = by_id.get(item.task_id)
                if task is None or task.requirement != item.requirement:
                    raise CheckpointError(f"{role} has unknown or mismatched task {item.task_id}")
                is_scholarly = task.lane.value == "SCHOLARLY_FULLTEXT"
                if is_scholarly != (role == "scholarly_evidence"):
                    raise CheckpointError(f"{role} has incorrect lane for {item.task_id}")
    results = []
    for role in ("scholarly_evidence", "primary_evidence"):
        run = parsed.get(role)
        if run is not None:
            results.extend(item.evidence_result for item in run.task_results)
    ids = [item.requirement_id for item in results]
    if len(ids) != len(set(ids)):
        raise CheckpointError("duplicate evidence requirement across lanes")
    research = parsed.get("research_draft")
    evidence_task_ids = {
        item.task_id
        for role in ("scholarly_evidence", "primary_evidence")
        for item in getattr(parsed.get(role), "task_results", ())
    }
    complete_plan = (
        plan is not None
        and evidence_task_ids == {task.task_id for task in plan.tasks}
    )
    # Partial snapshots are valid. Do not claim full research/evidence linkage
    # until every planned verification task has a result.
    research_links_checked = research is not None and complete_plan
    if research_links_checked:
        from thesis_factory.research.proposal_research import validate_research_draft
        validate_research_draft(research, evidence_results=tuple(results))
    document = parsed.get("document_draft")
    if document is not None and research is not None:
        from thesis_factory.research.proposal_writing import validate_proposal_document
        validate_proposal_document(document, research=research)
    return {
        "topic": next(iter(topics)) if topics else None,
        "evidence_results": len(results),
        "verified_spans": sum(len(result.evidence) for result in results),
        "evidence_statuses": {
            state: sum(result.status.value == state for result in results)
            for state in ("SUPPORTED", "PARTIAL", "NOT_SUPPORTED", "INSUFFICIENT_EVIDENCE")
        },
        "research_findings": len(research.findings) if research is not None else None,
        "research_links": "VALIDATED" if research_links_checked else "DEFERRED",
    }


def create_research_checkpoint(*, root: Path, run_id: str,
                               artifacts: dict[str, Path]) -> dict[str, Any]:
    if not artifacts:
        raise CheckpointError("at least one artifact required")
    if set(artifacts) - set(ROLES):
        raise CheckpointError("unknown artifact role")
    # First validate ALL data. No partial checkpoint is emitted on failure.
    parsed = {}
    sources: dict[str, tuple[Path, bytes, str]] = {}
    for role, input_path in artifacts.items():
        path = input_path.resolve(strict=True)
        if not path.is_file():
            raise CheckpointError(f"{role} is not a file")
        size = path.stat().st_size
        if size < 2 or size > MAX_ARTIFACT_BYTES:
            raise CheckpointError(f"{role} artifact size outside limits")
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        parsed[role] = _parse_role(role, path)
        sources[role] = (path, data, digest)
    summary = _check_linkage(parsed)
    run_dir = create_run_directory(root, run_id)
    store = run_dir / "artifacts"
    store.mkdir(exist_ok=True, mode=0o700)
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "created_at_utc": utc_now(),
        "validation": "LOCAL_SCHEMA_AND_IDENTITY_ONLY",
        "research_summary": summary,
        "artifacts": {},
    }
    for role, (path, data, digest) in sources.items():
        target = store / f"{digest}.json"
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise CheckpointError("artifact store hash collision / corruption")
        else:
            # Exclusive create: content-addressed bytes cannot be overwritten.
            fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        manifest["artifacts"][role] = {
            "sha256": digest,
            "size_bytes": len(data),
            "stored_filename": f"artifacts/{digest}.json",
            "original_filename": path.name,
        }
    # One immutable checkpoint manifest per run invocation; later runs do not
    # overwrite old manifests, and can coexist with journal stage attempts.
    manifests = run_dir / "checkpoints"
    manifests.mkdir(exist_ok=True, mode=0o700)
    existing = sorted(manifests.glob("checkpoint-*.json"))
    next_id = len(existing) + 1
    name = f"checkpoint-{next_id:04d}.json"
    target = manifests / name
    if target.exists():
        raise CheckpointError("checkpoint number conflict")
    write_json_atomically(target, manifest)
    append_event(run_dir, run_id, "research_checkpoint", "CHECKPOINT_CREATED", metadata={
        "checkpoint": next_id, "artifacts": len(sources),
        "evidence_results": summary["evidence_results"],
        "verified_spans": summary["verified_spans"],
    })
    return manifest
