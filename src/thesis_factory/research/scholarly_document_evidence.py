from thesis_factory.domain.document import (
    NormalizedDocument,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.evidence.context import (
    expand_retrieval_context,
)
from thesis_factory.evidence.extraction import (
    EvidenceExtractor,
    verify_extraction_proposal,
)
from thesis_factory.research.scholarly_evidence_execution import (
    DocumentEvidenceOutcome,
)
from thesis_factory.retrieval.bm25 import (
    BM25Retriever,
)
from thesis_factory.retrieval.corpus import (
    build_retrieval_units,
)
from thesis_factory.retrieval.semantic import (
    SemanticRetriever,
)


_STATUS_RANK = {
    EvidenceSupportStatus.INSUFFICIENT_EVIDENCE: 0,
    EvidenceSupportStatus.NOT_SUPPORTED: 1,
    EvidenceSupportStatus.PARTIAL: 2,
    EvidenceSupportStatus.SUPPORTED: 3,
}


class VoyageDocumentEvidenceFinder:
    def __init__(
        self,
        *,
        embedder,
        extractor: EvidenceExtractor,
        bm25_candidates: int = 24,
        semantic_hits: int = 4,
        extraction_hits: int = 2,
    ) -> None:
        if bm25_candidates < 1:
            raise ValueError(
                "bm25_candidates must be positive"
            )

        if semantic_hits < 1:
            raise ValueError(
                "semantic_hits must be positive"
            )

        if extraction_hits < 1:
            raise ValueError(
                "extraction_hits must be positive"
            )

        self._embedder = embedder
        self._extractor = extractor
        self._bm25_candidates = (
            bm25_candidates
        )
        self._semantic_hits = (
            semantic_hits
        )
        self._extraction_hits = (
            extraction_hits
        )

    def find(
        self,
        *,
        requirement: EvidenceRequirement,
        document: NormalizedDocument,
    ) -> DocumentEvidenceOutcome:
        units = build_retrieval_units(
            document
        )

        if not units:
            return DocumentEvidenceOutcome(
                result=_insufficient(
                    requirement,
                    (
                        "Normalized document produced "
                        "no retrieval units."
                    ),
                ),
            )

        bm25 = BM25Retriever(
            units
        )

        lexical_hits = bm25.search(
            requirement.question,
            top_k=min(
                self._bm25_candidates,
                len(units),
            ),
        )

        candidate_units = tuple(
            hit.unit
            for hit in lexical_hits
        )

        if not candidate_units:
            candidate_units = units

        semantic = SemanticRetriever(
            candidate_units,
            embedder=self._embedder,
        )

        semantic_hits = semantic.search(
            requirement.question,
            top_k=min(
                self._semantic_hits,
                len(candidate_units),
            ),
        )

        best = _insufficient(
            requirement,
            (
                "Retrieved contexts did not "
                "establish the requirement."
            ),
        )

        errors: list[str] = []

        for hit in semantic_hits[
            :self._extraction_hits
        ]:
            try:
                context = (
                    expand_retrieval_context(
                        document,
                        hit,
                        neighbours_before=1,
                        neighbours_after=1,
                        cross_section=False,
                    )
                )

                proposal = (
                    self._extractor.propose(
                        requirement=(
                            requirement
                        ),
                        context=context,
                    )
                )

                result = (
                    verify_extraction_proposal(
                        document=document,
                        context=context,
                        requirement=requirement,
                        proposal=proposal,
                    )
                )
            except Exception as error:
                errors.append(
                    _error_text(
                        (
                            "Evidence extraction "
                            f"failed for paragraph "
                            f"{hit.unit.paragraph_ordinal}"
                        ),
                        error,
                    )
                )
                continue

            if (
                _STATUS_RANK[result.status]
                > _STATUS_RANK[best.status]
            ):
                best = result

            if (
                best.status
                == EvidenceSupportStatus.SUPPORTED
            ):
                break

        return DocumentEvidenceOutcome(
            result=best,
            errors=tuple(
                errors
            ),
        )


def _insufficient(
    requirement: EvidenceRequirement,
    rationale: str,
) -> VerifiedEvidenceResult:
    return VerifiedEvidenceResult(
        requirement_id=(
            requirement.requirement_id
        ),
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
    )[:1200]
