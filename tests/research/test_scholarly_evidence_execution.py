from hashlib import sha256

from thesis_factory.domain.document import (
    DocumentSectionKind,
    NormalizedDocument,
    NormalizedParagraph,
    NormalizedSection,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.domain.source import (
    SourceRecord,
)
from thesis_factory.research.scholarly_evidence_execution import (
    DocumentEvidenceOutcome,
    ScholarlyDocumentCandidate,
    ScholarlyDocumentDiscovery,
    ScholarlyEvidenceExecutor,
)


def _requirement():
    return EvidenceRequirement(
        requirement_id="req-1",
        kind=(
            EvidenceRequirementKind.BASELINE
        ),
        question="Does the paper support the baseline?",
        why_needed="Needed for model selection.",
    )


def _task():
    return ProposalVerificationTask(
        task_id="task-1",
        requirement=_requirement(),
        lane=(
            VerificationLane
            .SCHOLARLY_FULLTEXT
        ),
        priority=(
            VerificationPriority.HIGH
        ),
        lead_ids=("lead-1",),
        rationale="Verify it.",
    )


def _source(index):
    return SourceRecord(
        title=f"Paper {index}",
        authors=("A. Author",),
        publication_year=2025,
        doi=f"10.1000/{index}",
        provider="openalex",
        provider_id=(
            f"https://openalex.org/W{index}"
        ),
    )


def _document(index):
    digest = sha256(
        f"document-{index}".encode()
    ).hexdigest()

    return NormalizedDocument(
        artifact_sha256=digest,
        source_provider="openalex",
        source_provider_id=(
            f"https://openalex.org/W{index}"
        ),
        sections=(
            NormalizedSection(
                ordinal=1,
                kind=(
                    DocumentSectionKind.BODY
                ),
                path=("Results",),
                paragraphs=(
                    NormalizedParagraph(
                        ordinal=1,
                        text=(
                            "The baseline performed "
                            "competitively."
                        ),
                    ),
                ),
            ),
        ),
    )


class FakeProvider:
    def __init__(
        self,
        documents,
    ):
        self.documents = documents

    def discover(
        self,
        *,
        requirement,
    ):
        return ScholarlyDocumentDiscovery(
            documents=self.documents,
            source_audits=(),
        )


class FakeFinder:
    def __init__(
        self,
        statuses,
    ):
        self.statuses = list(
            statuses
        )
        self.calls = 0

    def find(
        self,
        *,
        requirement,
        document,
    ):
        status = self.statuses[
            self.calls
        ]
        self.calls += 1

        return DocumentEvidenceOutcome(
            result=VerifiedEvidenceResult(
                requirement_id=(
                    requirement.requirement_id
                ),
                status=status,
                rationale=(
                    f"status {status.value}"
                ),
                evidence=(),
            ),
        )


def _candidate(index):
    return ScholarlyDocumentCandidate(
        source=_source(index),
        registry_source=_source(index),
        document=_document(index),
        fulltext_url=(
            f"https://example.org/{index}.xml"
        ),
    )


def test_executor_stops_after_supported_result() -> None:
    finder = FakeFinder(
        (
            EvidenceSupportStatus.PARTIAL,
            EvidenceSupportStatus.SUPPORTED,
            EvidenceSupportStatus.PARTIAL,
        )
    )

    executor = ScholarlyEvidenceExecutor(
        document_provider=(
            FakeProvider(
                (
                    _candidate(1),
                    _candidate(2),
                    _candidate(3),
                )
            )
        ),
        evidence_finder=finder,
    )

    result = executor.execute(
        task=_task()
    )

    assert (
        result.evidence_result.status
        == EvidenceSupportStatus.SUPPORTED
    )
    assert finder.calls == 2


def test_executor_returns_insufficient_with_no_documents() -> None:
    executor = ScholarlyEvidenceExecutor(
        document_provider=(
            FakeProvider(())
        ),
        evidence_finder=(
            FakeFinder(())
        ),
    )

    result = executor.execute(
        task=_task()
    )

    assert (
        result.evidence_result.status
        == EvidenceSupportStatus
        .INSUFFICIENT_EVIDENCE
    )
