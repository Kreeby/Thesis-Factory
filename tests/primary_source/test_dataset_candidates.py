from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.primary_source.dataset_candidates import (
    deterministic_dataset_candidates,
)


def _task(
    question,
):
    return ProposalVerificationTask(
        task_id="task-1",
        requirement=EvidenceRequirement(
            requirement_id="req-1",
            kind=(
                EvidenceRequirementKind.DATASET
            ),
            question=question,
            why_needed="Verify from primary source.",
        ),
        lane=(
            VerificationLane.DATASET_PRIMARY
        ),
        priority=(
            VerificationPriority.CRITICAL
        ),
        lead_ids=("lead-1",),
        rationale="Required.",
    )


def test_routes_known_dataset_candidates() -> None:
    fico = deterministic_dataset_candidates(
        _task(
            "Verify FICO HELOC benchmark."
        )
    )
    german = deterministic_dataset_candidates(
        _task(
            "Verify Statlog German Credit."
        )
    )
    home = deterministic_dataset_candidates(
        _task(
            "Verify Home Credit Default Risk Kaggle."
        )
    )

    assert (
        "community.fico.com"
        in fico[0].url
    )
    assert (
        "/dataset/144/"
        in german[0].url
    )
    assert (
        "/dataset/573/"
        in german[1].url
    )
    assert home[0].url.endswith(
        "/home-credit-default-risk/data"
    )
