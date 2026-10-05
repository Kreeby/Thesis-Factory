from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
    EvidenceSupportStatus,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.primary_source.execution import (
    PrimarySourceExecutor,
)


class FailingScout:
    def discover(
        self,
        *,
        topic,
        task,
    ):
        raise ValueError(
            "provider failure"
        )


class UnusedFetcher:
    def fetch(
        self,
        **kwargs,
    ):
        raise AssertionError(
            "must not fetch"
        )


class UnusedFinder:
    def find(
        self,
        **kwargs,
    ):
        raise AssertionError(
            "must not extract"
        )


def test_discovery_failure_becomes_task_result() -> None:
    task = ProposalVerificationTask(
        task_id="task-1",
        requirement=EvidenceRequirement(
            requirement_id="req-1",
            kind=(
                EvidenceRequirementKind.LEGAL
            ),
            question="Verify primary law.",
            why_needed="Needed.",
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

    result = (
        PrimarySourceExecutor(
            scout=FailingScout(),
            fetcher=UnusedFetcher(),
            evidence_finder=UnusedFinder(),
        )
        .execute(
            topic="Topic",
            task=task,
        )
    )

    assert (
        result.evidence_result.status
        == EvidenceSupportStatus
        .INSUFFICIENT_EVIDENCE
    )
    assert len(result.errors) == 1
    assert "provider failure" in result.errors[0]
