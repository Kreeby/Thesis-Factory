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


def _task(
    question: str,
    why_needed: str = "Verify primary law.",
):
    return ProposalVerificationTask(
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


def test_resolves_cjeu_case_to_cellar_primary_content() -> None:
    candidates = (
        deterministic_legal_candidates(
            _task(
                "Verify C-203/22 judgment."
            )
        )
    )

    assert candidates[0].url == (
        "https://publications.europa.eu/"
        "resource/celex/62022CJ0203"
        "?language=eng"
    )


def test_resolves_directive_and_ai_act_alias() -> None:
    directive = (
        deterministic_legal_candidates(
            _task(
                "Verify Directive 2023/2225."
            )
        )
    )

    assert "32023L2225" in (
        directive[0].url
    )

    ai_act = (
        deterministic_legal_candidates(
            _task(
                "Verify AI Act Annex III."
            )
        )
    )

    assert "32024R1689" in (
        ai_act[0].url
    )
