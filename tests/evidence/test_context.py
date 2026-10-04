import pytest

from thesis_factory.domain.document import (
    DocumentSectionKind,
    NormalizedDocument,
    NormalizedParagraph,
    NormalizedSection,
)
from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnit,
)
from thesis_factory.evidence.context import (
    EvidenceContextError,
    expand_retrieval_context,
)


SHA256 = "a" * 64


def _document() -> NormalizedDocument:
    return NormalizedDocument(
        artifact_sha256=SHA256,
        source_provider="openalex",
        source_provider_id="W1",
        sections=(
            NormalizedSection(
                ordinal=1,
                kind=DocumentSectionKind.BODY,
                path=("One",),
                paragraphs=(
                    NormalizedParagraph(
                        ordinal=1,
                        text="Paragraph one.",
                    ),
                    NormalizedParagraph(
                        ordinal=2,
                        text="Paragraph two.",
                    ),
                    NormalizedParagraph(
                        ordinal=3,
                        text="Paragraph three.",
                    ),
                ),
            ),
            NormalizedSection(
                ordinal=2,
                kind=DocumentSectionKind.BODY,
                path=("Two",),
                paragraphs=(
                    NormalizedParagraph(
                        ordinal=4,
                        text="Paragraph four.",
                    ),
                ),
            ),
        ),
    )


def _hit(
    *,
    paragraph_ordinal: int = 2,
    text: str = "Paragraph two.",
) -> RetrievalHit:
    document = _document()

    section = next(
        section
        for section in document.sections
        if any(
            paragraph.ordinal
            == paragraph_ordinal
            for paragraph in section.paragraphs
        )
    )

    return RetrievalHit(
        unit=RetrievalUnit(
            artifact_sha256=SHA256,
            normalization_version="grobid-tei-v1",
            source_provider="openalex",
            source_provider_id="W1",
            section_ordinal=section.ordinal,
            section_path=section.path,
            section_kind=section.kind,
            heading_role=section.heading_role,
            paragraph_ordinal=paragraph_ordinal,
            text=text,
        ),
        score=0.9,
    )


def test_expands_neighbours_inside_section() -> None:
    context = expand_retrieval_context(
        _document(),
        _hit(),
        neighbours_before=1,
        neighbours_after=1,
    )

    assert [
        unit.paragraph_ordinal
        for unit in context.units
    ] == [1, 2, 3]

    assert (
        context.hit_identity
        == _hit().unit.identity
    )


def test_does_not_cross_section_by_default() -> None:
    context = expand_retrieval_context(
        _document(),
        _hit(paragraph_ordinal=3, text="Paragraph three."),
        neighbours_before=0,
        neighbours_after=2,
    )

    assert [
        unit.paragraph_ordinal
        for unit in context.units
    ] == [3]


def test_can_cross_section_explicitly() -> None:
    context = expand_retrieval_context(
        _document(),
        _hit(paragraph_ordinal=3, text="Paragraph three."),
        neighbours_before=0,
        neighbours_after=1,
        cross_section=True,
    )

    assert [
        unit.paragraph_ordinal
        for unit in context.units
    ] == [3, 4]


def test_rejects_negative_window() -> None:
    with pytest.raises(
        ValueError,
        match="must not be negative",
    ):
        expand_retrieval_context(
            _document(),
            _hit(),
            neighbours_before=-1,
        )


def test_rejects_tampered_hit_content() -> None:
    with pytest.raises(
        EvidenceContextError,
        match="does not match",
    ):
        expand_retrieval_context(
            _document(),
            _hit(
                text="Tampered paragraph.",
            ),
        )
