import pytest
from pydantic import ValidationError

from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationPlan,
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)


def _task(
    *,
    task_id="task-1",
    requirement_id="req-1",
    lead_ids=("lead-1",),
):
    return ProposalVerificationTask(
        task_id=task_id,
        requirement=EvidenceRequirement(
            requirement_id=requirement_id,
            kind=(
                EvidenceRequirementKind
                .LITERATURE
            ),
            question="What must be verified?",
            why_needed="Needed for the proposal.",
        ),
        lane=(
            VerificationLane
            .SCHOLARLY_FULLTEXT
        ),
        priority=(
            VerificationPriority
            .CRITICAL
        ),
        lead_ids=lead_ids,
        rationale="Verify the core claim.",
    )


def test_plan_rejects_duplicate_task_ids() -> None:
    with pytest.raises(
        ValidationError,
        match="task ids must be unique",
    ):
        ProposalVerificationPlan(
            topic="Topic",
            tasks=(
                _task(),
                _task(
                    requirement_id="req-2",
                    lead_ids=("lead-2",),
                ),
            ),
            deferral_rationale="None deferred.",
        )


def test_plan_rejects_lead_in_two_tasks() -> None:
    with pytest.raises(
        ValidationError,
        match="only one verification task",
    ):
        ProposalVerificationPlan(
            topic="Topic",
            tasks=(
                _task(),
                _task(
                    task_id="task-2",
                    requirement_id="req-2",
                    lead_ids=("lead-1",),
                ),
            ),
            deferral_rationale="None deferred.",
        )


def test_plan_rejects_scheduled_and_deferred_overlap() -> None:
    with pytest.raises(
        ValidationError,
        match="both scheduled and deferred",
    ):
        ProposalVerificationPlan(
            topic="Topic",
            tasks=(
                _task(),
            ),
            deferred_lead_ids=(
                "lead-1",
            ),
            deferral_rationale="Deferred.",
        )
