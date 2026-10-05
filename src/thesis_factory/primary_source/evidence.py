from thesis_factory.domain.document import (
    DocumentSectionKind,
    SectionHeadingRole,
)
from thesis_factory.domain.evidence import (
    EvidenceAddress,
    EvidenceSpan,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceContext,
    EvidenceExtractionProposal,
    EvidenceRequirement,
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.domain.primary_source import (
    PrimarySourceDocument,
)
from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnit,
)
from thesis_factory.evidence.extraction import (
    EvidenceExtractor,
)
from thesis_factory.retrieval.bm25 import (
    BM25Retriever,
)
from thesis_factory.retrieval.semantic import (
    SemanticRetriever,
)


class PrimaryEvidenceError(
    ValueError
):
    pass


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


class PrimaryDocumentEvidenceFinder:
    def __init__(
        self,
        *,
        embedder,
        extractor: EvidenceExtractor,
        bm25_candidates: int = 40,
        semantic_hits: int = 5,
        extraction_hits: int = 4,
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
        document: PrimarySourceDocument,
    ) -> VerifiedEvidenceResult:
        units = _document_units(
            document
        )

        bm25 = BM25Retriever(
            units
        )

        candidate_by_identity = {}

        for query in _retrieval_queries(
            requirement
        ):
            lexical_hits = bm25.search(
                query,
                top_k=min(
                    self._bm25_candidates,
                    len(units),
                ),
            )

            for hit in lexical_hits:
                candidate_by_identity.setdefault(
                    hit.unit.identity,
                    hit.unit,
                )

        candidate_units = tuple(
            candidate_by_identity.values()
        )

        if not candidate_units:
            candidate_units = units

        semantic_hits_by_identity = {}

        for query in _retrieval_queries(
            requirement
        ):
            semantic = SemanticRetriever(
                candidate_units,
                embedder=self._embedder,
            )

            hits = semantic.search(
                query,
                top_k=min(
                    self._semantic_hits,
                    len(candidate_units),
                ),
            )

            for hit in hits:
                semantic_hits_by_identity.setdefault(
                    hit.unit.identity,
                    hit,
                )

        semantic_hits = tuple(
            semantic_hits_by_identity.values()
        )

        best = _insufficient(
            requirement,
            (
                "Retrieved primary-source contexts "
                "did not establish the requirement."
            ),
        )

        for hit in semantic_hits[
            :self._extraction_hits
        ]:
            context = _expand_context(
                units,
                hit,
                neighbours_before=1,
                neighbours_after=1,
            )

            proposal = (
                self._extractor.propose(
                    requirement=requirement,
                    context=context,
                )
            )

            result = (
                verify_primary_proposal(
                    document=document,
                    context=context,
                    requirement=requirement,
                    proposal=proposal,
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

        return best


def _retrieval_queries(
    requirement: EvidenceRequirement,
) -> tuple[
    str,
    ...,
]:
    return tuple(
        dict.fromkeys(
            value
            for value in (
                " ".join(
                    requirement.question.split()
                ),
                " ".join(
                    requirement.why_needed.split()
                ),
            )
            if value
        )
    )


def verify_primary_proposal(
    *,
    document: PrimarySourceDocument,
    context: EvidenceContext,
    requirement: EvidenceRequirement,
    proposal: EvidenceExtractionProposal,
) -> VerifiedEvidenceResult:
    if (
        proposal.requirement_id
        != requirement.requirement_id
    ):
        raise PrimaryEvidenceError(
            "proposal targets a different "
            "requirement"
        )

    context_by_ordinal = {
        unit.paragraph_ordinal: unit
        for unit in context.units
    }

    verified: list[
        EvidenceSpan
    ] = []

    for quote in proposal.quotes:
        unit = context_by_ordinal.get(
            quote.paragraph_ordinal
        )

        if unit is None:
            raise PrimaryEvidenceError(
                "proposal references paragraph "
                "outside supplied context"
            )

        first_index = unit.text.find(
            quote.exact_quote
        )

        if first_index < 0:
            raise PrimaryEvidenceError(
                "proposed quote is not an exact "
                "substring of the paragraph"
            )

        second_index = unit.text.find(
            quote.exact_quote,
            first_index + 1,
        )

        if second_index >= 0:
            raise PrimaryEvidenceError(
                "proposed quote occurs more than "
                "once in the paragraph"
            )

        address = EvidenceAddress(
            artifact_sha256=(
                document.artifact_sha256
            ),
            normalization_version=(
                document.normalization_version
            ),
            paragraph_ordinal=(
                quote.paragraph_ordinal
            ),
            start_char=first_index,
            end_char=(
                first_index
                + len(
                    quote.exact_quote
                )
            ),
        )

        verified.append(
            _resolve_span(
                document,
                address,
            )
        )

    if (
        proposal.status
        in {
            EvidenceSupportStatus
            .SUPPORTED,
            EvidenceSupportStatus
            .PARTIAL,
        }
        and not verified
    ):
        raise PrimaryEvidenceError(
            "supporting proposal produced "
            "no verified evidence"
        )

    return VerifiedEvidenceResult(
        requirement_id=(
            requirement.requirement_id
        ),
        status=proposal.status,
        rationale=proposal.rationale,
        evidence=tuple(
            verified
        ),
    )


def _document_units(
    document: PrimarySourceDocument,
) -> tuple[
    RetrievalUnit,
    ...,
]:
    return tuple(
        RetrievalUnit(
            artifact_sha256=(
                document.artifact_sha256
            ),
            normalization_version=(
                document.normalization_version
            ),
            source_provider="primary_web",
            source_provider_id=(
                document.source_url
            ),
            section_ordinal=1,
            section_path=(
                "Primary source",
            ),
            section_kind=(
                DocumentSectionKind.BODY
            ),
            heading_role=(
                SectionHeadingRole.STANDARD
            ),
            paragraph_ordinal=(
                paragraph.ordinal
            ),
            text=paragraph.text,
        )
        for paragraph
        in document.paragraphs
    )


def _expand_context(
    units: tuple[
        RetrievalUnit,
        ...,
    ],
    hit: RetrievalHit,
    *,
    neighbours_before: int,
    neighbours_after: int,
) -> EvidenceContext:
    hit_index = None

    for index, unit in enumerate(
        units
    ):
        if (
            unit.identity
            == hit.unit.identity
        ):
            if unit != hit.unit:
                raise PrimaryEvidenceError(
                    "retrieval hit does not "
                    "match primary document"
                )

            hit_index = index
            break

    if hit_index is None:
        raise PrimaryEvidenceError(
            "retrieval hit not found in "
            "primary document"
        )

    lower = max(
        0,
        hit_index
        - neighbours_before,
    )

    upper = min(
        len(units),
        hit_index
        + neighbours_after
        + 1,
    )

    return EvidenceContext(
        hit_identity=(
            hit.unit.identity
        ),
        units=units[
            lower:
            upper
        ],
    )


def _resolve_span(
    document: PrimarySourceDocument,
    address: EvidenceAddress,
) -> EvidenceSpan:
    if (
        address.artifact_sha256
        != document.artifact_sha256
    ):
        raise PrimaryEvidenceError(
            "evidence address targets "
            "a different primary artifact"
        )

    if (
        address.normalization_version
        != document.normalization_version
    ):
        raise PrimaryEvidenceError(
            "evidence address uses a different "
            "normalization version"
        )

    paragraph = next(
        (
            item
            for item
            in document.paragraphs
            if (
                item.ordinal
                == address.paragraph_ordinal
            )
        ),
        None,
    )

    if paragraph is None:
        raise PrimaryEvidenceError(
            "primary paragraph does not exist"
        )

    if (
        address.end_char
        > len(paragraph.text)
    ):
        raise PrimaryEvidenceError(
            "evidence range exceeds "
            "primary paragraph length"
        )

    text = paragraph.text[
        address.start_char:
        address.end_char
    ]

    if not text:
        raise PrimaryEvidenceError(
            "evidence span resolved to "
            "empty text"
        )

    return EvidenceSpan(
        address=address,
        text=text,
        source_provider="primary_web",
        source_provider_id=(
            document.source_url
        ),
        section_ordinal=1,
        section_path=(
            "Primary source",
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
