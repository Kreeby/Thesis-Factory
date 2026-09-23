from thesis_factory.domain.document import (
    DocumentSectionKind,
    NormalizedDocument,
    NormalizedParagraph,
    NormalizedSection,
    SectionHeadingRole,
)
from thesis_factory.retrieval.corpus import (
    build_retrieval_units,
)


SHA256 = "a" * 64


def _document() -> NormalizedDocument:
    return NormalizedDocument(
        artifact_sha256=SHA256,
        source_provider="openalex",
        source_provider_id=(
            "https://openalex.org/W123"
        ),
        sections=(
            NormalizedSection(
                ordinal=1,
                kind=(
                    DocumentSectionKind
                    .ABSTRACT
                ),
                path=("Abstract",),
                paragraphs=(
                    NormalizedParagraph(
                        ordinal=1,
                        text="Abstract text.",
                    ),
                ),
            ),
            NormalizedSection(
                ordinal=2,
                kind=(
                    DocumentSectionKind
                    .BODY
                ),
                heading_role=(
                    SectionHeadingRole
                    .TABLE
                ),
                path=(
                    "Table 1: Results",
                ),
                paragraphs=(
                    NormalizedParagraph(
                        ordinal=2,
                        text="First result.",
                    ),
                    NormalizedParagraph(
                        ordinal=3,
                        text="Second result.",
                    ),
                ),
            ),
        ),
    )


def test_builds_one_unit_per_paragraph() -> None:
    units = build_retrieval_units(
        _document()
    )

    assert len(units) == 3

    assert [
               unit.paragraph_ordinal
               for unit in units
           ] == [
               1,
               2,
               3,
           ]


def test_preserves_paragraph_text_exactly() -> None:
    units = build_retrieval_units(
        _document()
    )

    assert (
            units[1].text
            == "First result."
    )


def test_preserves_provenance_and_structure() -> None:
    units = build_retrieval_units(
        _document()
    )

    unit = units[1]

    assert (
            unit.artifact_sha256
            == SHA256
    )

    assert (
            unit.normalization_version
            == "grobid-tei-v1"
    )

    assert (
            unit.source_provider
            == "openalex"
    )

    assert (
            unit.section_ordinal
            == 2
    )

    assert unit.section_path == (
        "Table 1: Results",
    )

    assert (
            unit.heading_role
            == SectionHeadingRole.TABLE
    )