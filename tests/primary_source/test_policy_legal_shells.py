from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.domain.primary_source import (
    PrimarySourceCandidate,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.primary_source.policy import (
    candidate_is_authoritative,
)


def _task():
    return ProposalVerificationTask(
        task_id="task-1",
        requirement=EvidenceRequirement(
            requirement_id="req-1",
            kind=(
                EvidenceRequirementKind.LEGAL
            ),
            question="Verify C-634/21.",
            why_needed="Read judgment.",
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


def test_rejects_infocuria_shell_but_accepts_direct_juris() -> None:
    task = _task()

    assert not candidate_is_authoritative(
        task,
        PrimarySourceCandidate(
            url=(
                "https://infocuria.curia.europa.eu/"
                "tabs/redirect/juris/liste.jsf"
                "?num=C-634%2F21"
            ),
        ),
    )

    assert candidate_is_authoritative(
        task,
        PrimarySourceCandidate(
            url=(
                "https://juris.curia.europa.eu/"
                "juris/document/document.jsf"
                "?docid=123"
            ),
        ),
    )
