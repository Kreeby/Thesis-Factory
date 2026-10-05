from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.domain.primary_source import (
    PrimarySourceCandidate,
    PrimarySourceDocument,
    PrimarySourceParagraph,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.primary_source.execution import (
    PrimarySourceExecutor,
)


def _task():
    return ProposalVerificationTask(
        task_id="task-1",
        requirement=EvidenceRequirement(
            requirement_id="req-1",
            kind=(
                EvidenceRequirementKind.LEGAL
            ),
            question=(
                "Verify Directive 2023/2225."
            ),
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


class FakeScout:
    def discover(
        self,
        *,
        topic,
        task,
    ):
        return (
            PrimarySourceCandidate(
                url=(
                    "https://example.com/blog"
                ),
                title="Blog",
            ),
            PrimarySourceCandidate(
                url=(
                    "https://eur-lex.europa.eu/"
                    "eli/dir/2023/2225/oj/eng"
                ),
                title="Directive",
            ),
        )


class FakeFetcher:
    def fetch(
        self,
        *,
        url,
        title=None,
    ):
        return PrimarySourceDocument(
            artifact_sha256=(
                "a" * 64
            ),
            source_url=url,
            source_host=(
                "eur-lex.europa.eu"
            ),
            title=title,
            paragraphs=(
                PrimarySourceParagraph(
                    ordinal=1,
                    text=(
                        "Official source text."
                    ),
                ),
            ),
        )


class FakeFinder:
    def find(
        self,
        *,
        requirement,
        document,
    ):
        return VerifiedEvidenceResult(
            requirement_id=(
                requirement.requirement_id
            ),
            status=(
                EvidenceSupportStatus.PARTIAL
            ),
            rationale="Partially supported.",
            evidence=(),
        )


def test_executor_rejects_secondary_and_uses_official() -> None:
    result = (
        PrimarySourceExecutor(
            scout=FakeScout(),
            fetcher=FakeFetcher(),
            evidence_finder=FakeFinder(),
        )
        .execute(
            topic="Topic",
            task=_task(),
        )
    )

    assert (
        result.evidence_result.status
        == EvidenceSupportStatus.PARTIAL
    )

    assert (
        result.sources[0]
        .authority_accepted
        is False
    )

    assert (
        result.sources[1]
        .fetched
        is True
    )
