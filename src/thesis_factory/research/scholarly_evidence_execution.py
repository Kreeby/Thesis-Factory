from dataclasses import dataclass
from typing import Protocol

from thesis_factory.domain.document import (
    NormalizedDocument,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
)
from thesis_factory.domain.scholarly_verification import (
    ScholarlySourceAudit,
    ScholarlyTaskVerification,
)
from thesis_factory.domain.source import (
    SourceRecord,
)


@dataclass(
    frozen=True,
)
class ScholarlyDocumentCandidate:
    source: SourceRecord
    registry_source: SourceRecord | None
    document: NormalizedDocument
    fulltext_url: str


@dataclass(
    frozen=True,
)
class ScholarlyDocumentDiscovery:
    documents: tuple[
        ScholarlyDocumentCandidate,
        ...,
    ]

    source_audits: tuple[
        ScholarlySourceAudit,
        ...,
    ]

    errors: tuple[
        str,
        ...,
    ] = ()


@dataclass(
    frozen=True,
)
class DocumentEvidenceOutcome:
    result: VerifiedEvidenceResult

    errors: tuple[
        str,
        ...,
    ] = ()


class ScholarlyDocumentProvider(
    Protocol
):
    def discover(
        self,
        *,
        requirement,
    ) -> ScholarlyDocumentDiscovery:
        ...


class DocumentEvidenceFinder(
    Protocol
):
    def find(
        self,
        *,
        requirement,
        document: NormalizedDocument,
    ) -> DocumentEvidenceOutcome:
        ...


_STATUS_RANK = {
    EvidenceSupportStatus.INSUFFICIENT_EVIDENCE: 0,
    EvidenceSupportStatus.NOT_SUPPORTED: 1,
    EvidenceSupportStatus.PARTIAL: 2,
    EvidenceSupportStatus.SUPPORTED: 3,
}


class ScholarlyEvidenceExecutor:
    def __init__(
        self,
        *,
        document_provider: ScholarlyDocumentProvider,
        evidence_finder: DocumentEvidenceFinder,
    ) -> None:
        self._document_provider = (
            document_provider
        )
        self._evidence_finder = (
            evidence_finder
        )

    def execute(
        self,
        *,
        task: ProposalVerificationTask,
    ) -> ScholarlyTaskVerification:
        discovery = (
            self._document_provider
            .discover(
                requirement=task.requirement,
            )
        )

        errors = list(
            discovery.errors
        )

        best = _insufficient_result(
            task.requirement.requirement_id,
            (
                "No verified scholarly full-text "
                "evidence has supported the "
                "requirement yet."
            ),
        )

        for candidate in discovery.documents:
            try:
                outcome = (
                    self._evidence_finder
                    .find(
                        requirement=(
                            task.requirement
                        ),
                        document=(
                            candidate.document
                        ),
                    )
                )
            except Exception as error:
                errors.append(
                    _error_text(
                        (
                            "evidence extraction failed "
                            f"for {candidate.source.provider_id}"
                        ),
                        error,
                    )
                )
                continue

            errors.extend(
                outcome.errors
            )

            if (
                _STATUS_RANK[
                    outcome.result.status
                ]
                > _STATUS_RANK[
                    best.status
                ]
            ):
                best = outcome.result

            if (
                best.status
                == EvidenceSupportStatus.SUPPORTED
            ):
                break

        return ScholarlyTaskVerification(
            task_id=task.task_id,
            requirement=task.requirement,
            evidence_result=best,
            sources=discovery.source_audits,
            errors=tuple(
                errors
            ),
        )


def _insufficient_result(
    requirement_id: str,
    rationale: str,
) -> VerifiedEvidenceResult:
    return VerifiedEvidenceResult(
        requirement_id=requirement_id,
        status=(
            EvidenceSupportStatus
            .INSUFFICIENT_EVIDENCE
        ),
        rationale=rationale,
        evidence=(),
    )


def _error_text(
    context: str,
    error: Exception,
) -> str:
    message = " ".join(
        str(error).split()
    )

    if not message:
        message = (
            error.__class__.__name__
        )

    return (
        f"{context}: "
        f"{error.__class__.__name__}: "
        f"{message}"
    )[:1500]
