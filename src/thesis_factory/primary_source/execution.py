from typing import Protocol

from thesis_factory.domain.evidence_acquisition import (
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.domain.primary_source import (
    PrimarySourceAudit,
    PrimarySourceCandidate,
    PrimaryTaskVerification,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
)
from thesis_factory.primary_source.policy import (
    candidate_is_authoritative,
    source_host,
)


_STATUS_RANK = {
    EvidenceSupportStatus
    .INSUFFICIENT_EVIDENCE: 0,
    EvidenceSupportStatus
    .NOT_SUPPORTED: 1,
    EvidenceSupportStatus
    .PARTIAL: 2,
    EvidenceSupportStatus
    .SUPPORTED: 3,
}


class PrimarySourceScout(
    Protocol
):
    def discover(
        self,
        *,
        topic: str,
        task: ProposalVerificationTask,
    ) -> tuple[
        PrimarySourceCandidate,
        ...,
    ]:
        ...


class PrimaryDocumentFetcher(
    Protocol
):
    def fetch(
        self,
        *,
        url: str,
        title: str | None = None,
    ):
        ...


class PrimaryEvidenceFinder(
    Protocol
):
    def find(
        self,
        *,
        requirement,
        document,
    ) -> VerifiedEvidenceResult:
        ...


class PrimarySourceExecutor:
    def __init__(
        self,
        *,
        scout: PrimarySourceScout,
        fetcher: PrimaryDocumentFetcher,
        evidence_finder: PrimaryEvidenceFinder,
        max_documents: int = 2,
    ) -> None:
        if max_documents < 1:
            raise ValueError(
                "max_documents must be positive"
            )

        self._scout = scout
        self._fetcher = fetcher
        self._evidence_finder = (
            evidence_finder
        )
        self._max_documents = (
            max_documents
        )

    def execute(
        self,
        *,
        topic: str,
        task: ProposalVerificationTask,
    ) -> PrimaryTaskVerification:
        try:
            candidates = (
                self._scout.discover(
                    topic=topic,
                    task=task,
                )
            )
        except Exception as error:
            return PrimaryTaskVerification(
                task_id=task.task_id,
                requirement=task.requirement,
                evidence_result=VerifiedEvidenceResult(
                    requirement_id=(
                        task.requirement
                        .requirement_id
                    ),
                    status=(
                        EvidenceSupportStatus
                        .INSUFFICIENT_EVIDENCE
                    ),
                    rationale=(
                        "Primary-source discovery "
                        "failed before authoritative "
                        "evidence could be verified."
                    ),
                    evidence=(),
                ),
                sources=(),
                errors=(
                    _error_text(
                        "Primary-source discovery failed",
                        error,
                    ),
                ),
            )

        audits: list[
            PrimarySourceAudit
        ] = []

        errors: list[
            str
        ] = []

        best = VerifiedEvidenceResult(
            requirement_id=(
                task.requirement
                .requirement_id
            ),
            status=(
                EvidenceSupportStatus
                .INSUFFICIENT_EVIDENCE
            ),
            rationale=(
                "No authoritative primary source "
                "has established the requirement."
            ),
            evidence=(),
        )

        used_documents = 0
        seen_urls: set[
            str
        ] = set()

        for candidate in candidates:
            if candidate.url in seen_urls:
                continue

            seen_urls.add(
                candidate.url
            )

            host = source_host(
                candidate.url
            )

            accepted = (
                candidate_is_authoritative(
                    task,
                    candidate,
                )
            )

            if not accepted:
                audits.append(
                    PrimarySourceAudit(
                        url=candidate.url,
                        title=candidate.title,
                        host=(
                            host
                            or "unknown"
                        ),
                        authority_accepted=False,
                        fetched=False,
                        note=(
                            "Rejected by deterministic "
                            "primary-source authority "
                            "policy."
                        ),
                    )
                )
                continue

            if (
                used_documents
                >= self._max_documents
            ):
                break

            try:
                document = (
                    self._fetcher.fetch(
                        url=candidate.url,
                        title=candidate.title,
                    )
                )
            except Exception as error:
                audits.append(
                    PrimarySourceAudit(
                        url=candidate.url,
                        title=candidate.title,
                        host=(
                            host
                            or "unknown"
                        ),
                        authority_accepted=True,
                        fetched=False,
                        note=_error_text(
                            "Primary-source fetch failed",
                            error,
                        ),
                    )
                )
                continue

            used_documents += 1

            try:
                result = (
                    self._evidence_finder
                    .find(
                        requirement=(
                            task.requirement
                        ),
                        document=document,
                    )
                )
            except Exception as error:
                errors.append(
                    _error_text(
                        "Primary evidence extraction failed",
                        error,
                    )
                )

                audits.append(
                    PrimarySourceAudit(
                        url=candidate.url,
                        title=candidate.title,
                        host=document.source_host,
                        authority_accepted=True,
                        fetched=True,
                        artifact_sha256=(
                            document.artifact_sha256
                        ),
                        note=(
                            "Fetched and normalized, "
                            "but evidence extraction "
                            "failed."
                        ),
                    )
                )
                continue

            audits.append(
                PrimarySourceAudit(
                    url=candidate.url,
                    title=candidate.title,
                    host=document.source_host,
                    authority_accepted=True,
                    fetched=True,
                    artifact_sha256=(
                        document.artifact_sha256
                    ),
                    note=(
                        "Authoritative source fetched "
                        "and normalized."
                    ),
                )
            )

            if (
                _STATUS_RANK[
                    result.status
                ]
                > _STATUS_RANK[
                    best.status
                ]
            ):
                best = result

            if (
                best.status
                == EvidenceSupportStatus
                .SUPPORTED
            ):
                break

        return PrimaryTaskVerification(
            task_id=task.task_id,
            requirement=task.requirement,
            evidence_result=best,
            sources=tuple(
                audits
            ),
            errors=tuple(
                errors
            ),
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
