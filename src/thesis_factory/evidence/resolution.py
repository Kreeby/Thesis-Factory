from thesis_factory.domain.document import (
    NormalizedDocument,
    NormalizedParagraph,
    NormalizedSection,
)
from thesis_factory.domain.evidence import (
    EvidenceAddress,
    EvidenceSpan,
)


class EvidenceResolutionError(
    ValueError
):
    pass


def resolve_evidence_span(
        document: NormalizedDocument,
        address: EvidenceAddress,
) -> EvidenceSpan:
    _validate_document_identity(
        document,
        address,
    )

    section, paragraph = (
        _find_paragraph(
            document,
            address.paragraph_ordinal,
        )
    )

    if (
            address.end_char
            > len(paragraph.text)
    ):
        raise EvidenceResolutionError(
            "evidence character range "
            "exceeds paragraph length"
        )

    text = paragraph.text[
        address.start_char:
        address.end_char
    ]

    if not text:
        raise EvidenceResolutionError(
            "evidence span resolved to empty text"
        )

    return EvidenceSpan(
        address=address,
        text=text,
        source_provider=(
            document.source_provider
        ),
        source_provider_id=(
            document.source_provider_id
        ),
        section_ordinal=(
            section.ordinal
        ),
        section_path=(
            section.path
        ),
    )


def verify_evidence_span(
        document: NormalizedDocument,
        evidence: EvidenceSpan,
) -> None:
    resolved = resolve_evidence_span(
        document,
        evidence.address,
    )

    if resolved != evidence:
        raise EvidenceResolutionError(
            "evidence span does not match "
            "the normalized document"
        )


def _validate_document_identity(
        document: NormalizedDocument,
        address: EvidenceAddress,
) -> None:
    if (
            address.artifact_sha256
            != document.artifact_sha256
    ):
        raise EvidenceResolutionError(
            "evidence address targets "
            "a different artifact"
        )

    if (
            address.normalization_version
            != document.normalization_version
    ):
        raise EvidenceResolutionError(
            "evidence address targets "
            "a different normalization version"
        )


def _find_paragraph(
        document: NormalizedDocument,
        paragraph_ordinal: int,
) -> tuple[
    NormalizedSection,
    NormalizedParagraph,
]:
    for section in document.sections:
        for paragraph in section.paragraphs:
            if (
                    paragraph.ordinal
                    == paragraph_ordinal
            ):
                return (
                    section,
                    paragraph,
                )

    raise EvidenceResolutionError(
        "paragraph ordinal does not exist "
        "in normalized document"
    )