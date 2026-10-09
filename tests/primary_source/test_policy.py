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


def _task(
    *,
    lane,
    question,
):
    return ProposalVerificationTask(
        task_id="task-1",
        requirement=EvidenceRequirement(
            requirement_id="req-1",
            kind=(
                EvidenceRequirementKind.LEGAL
                if lane
                == VerificationLane
                .OFFICIAL_PRIMARY_WEB
                else EvidenceRequirementKind
                .DATASET
            ),
            question=question,
            why_needed="Verify from source.",
        ),
        lane=lane,
        priority=(
            VerificationPriority.CRITICAL
        ),
        lead_ids=("lead-1",),
        rationale="Required.",
    )


def _candidate(
    url,
):
    return PrimarySourceCandidate(
        url=url,
        title="Source",
    )


def test_legal_policy_accepts_eur_lex() -> None:
    task = _task(
        lane=(
            VerificationLane
            .OFFICIAL_PRIMARY_WEB
        ),
        question=(
            "Verify Directive 2023/2225."
        ),
    )

    assert candidate_is_authoritative(
        task,
        _candidate(
            "https://eur-lex.europa.eu/"
            "eli/dir/2023/2225/oj/eng"
        ),
    )

    assert not candidate_is_authoritative(
        task,
        _candidate(
            "https://example-law-blog.com/post"
        ),
    )


def test_dataset_policy_routes_known_candidates() -> None:
    fico = _task(
        lane=(
            VerificationLane
            .DATASET_PRIMARY
        ),
        question=(
            "Verify FICO HELOC dataset."
        ),
    )

    german = _task(
        lane=(
            VerificationLane
            .DATASET_PRIMARY
        ),
        question=(
            "Verify Statlog German Credit."
        ),
    )

    home = _task(
        lane=(
            VerificationLane
            .DATASET_PRIMARY
        ),
        question=(
            "Verify Home Credit Default Risk Kaggle."
        ),
    )

    assert candidate_is_authoritative(
        fico,
        _candidate(
            "https://community.fico.com/example"
        ),
    )

    assert candidate_is_authoritative(
        german,
        _candidate(
            "https://archive.ics.uci.edu/"
            "dataset/144/statlog+german+credit+data"
        ),
    )

    assert candidate_is_authoritative(
        home,
        _candidate(
            "https://www.kaggle.com/"
            "competitions/home-credit-default-risk"
        ),
    )
