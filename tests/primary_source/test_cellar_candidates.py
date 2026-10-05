from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.primary_source.legal_candidates import (
    deterministic_legal_candidates,
)


def test_cjeu_case_prefers_cellar_content_endpoint() -> None:
    task = ProposalVerificationTask(
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

    candidates = (
        deterministic_legal_candidates(
            task
        )
    )

    assert candidates[0].url == (
        "https://publications.europa.eu/"
        "resource/celex/62021CJ0634"
        "?language=eng"
    )

    assert candidates[1].url == (
        "https://eur-lex.europa.eu/"
        "legal-content/EN/TXT/"
        "?uri=CELEX:62021CJ0634"
    )
