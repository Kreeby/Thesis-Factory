import pytest
from pydantic import ValidationError

from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.domain.scholarly_verification import (
    ScholarlyTaskVerification,
    ScholarlyVerificationRun,
)


def _requirement():
    return EvidenceRequirement(
        requirement_id="req-1",
        kind=(
            EvidenceRequirementKind
            .LITERATURE
        ),
        question="What does the source establish?",
        why_needed="Needed for proposal.",
    )


def _task_result(
    task_id="task-1",
):
    return ScholarlyTaskVerification(
        task_id=task_id,
        requirement=_requirement(),
        evidence_result=(
            VerifiedEvidenceResult(
                requirement_id="req-1",
                status=(
                    EvidenceSupportStatus
                    .INSUFFICIENT_EVIDENCE
                ),
                rationale="Not enough evidence.",
                evidence=(),
            )
        ),
    )


def test_task_requires_matching_requirement_id() -> None:
    with pytest.raises(
        ValidationError,
        match="must match task requirement",
    ):
        ScholarlyTaskVerification(
            task_id="task-1",
            requirement=_requirement(),
            evidence_result=(
                VerifiedEvidenceResult(
                    requirement_id="different",
                    status=(
                        EvidenceSupportStatus
                        .INSUFFICIENT_EVIDENCE
                    ),
                    rationale="No evidence.",
                    evidence=(),
                )
            ),
        )


def test_run_rejects_duplicate_tasks() -> None:
    with pytest.raises(
        ValidationError,
        match="must be unique",
    ):
        ScholarlyVerificationRun(
            topic="Topic",
            task_results=(
                _task_result(),
                _task_result(),
            ),
        )
