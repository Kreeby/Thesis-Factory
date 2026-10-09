from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.integrations.anthropic.primary_source import (
    _build_bounded_objective,
)


def test_primary_source_objective_is_bounded() -> None:
    question = (
        "Verify whether a court judgment requires "
        "a detailed explanation of automated "
        "decision-making and the procedure used. "
        * 4
    )[:480]

    why_needed = (
        "Read the operative paragraphs and "
        "distinguish primary law from commentary, "
        "including the exact scope and limits. "
        * 5
    )[:480]

    task = ProposalVerificationTask(
        task_id="task-1",
        requirement=EvidenceRequirement(
            requirement_id="req-1",
            kind=(
                EvidenceRequirementKind.LEGAL
            ),
            question=question,
            why_needed=why_needed,
        ),
        lane=(
            VerificationLane
            .OFFICIAL_PRIMARY_WEB
        ),
        priority=(
            VerificationPriority.CRITICAL
        ),
        lead_ids=("lead-1",),
        rationale="Required.",
    )

    objective = (
        _build_bounded_objective(
            task
        )
    )

    assert len(objective) <= 1000
    assert "authoritative primary source" in objective
    assert "Requirement:" in objective
