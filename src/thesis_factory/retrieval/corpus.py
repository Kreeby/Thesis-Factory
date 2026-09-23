from thesis_factory.domain.document import (
    NormalizedDocument,
)
from thesis_factory.domain.retrieval import (
    RetrievalUnit,
    RetrievalUnitId,
)


def build_retrieval_units(
        document: NormalizedDocument,
) -> tuple[
    RetrievalUnit,
    ...
]:
    return tuple(
        RetrievalUnit(
            artifact_sha256=(
                document.artifact_sha256
            ),
            normalization_version=(
                document.normalization_version
            ),
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
            section_kind=(
                section.kind
            ),
            heading_role=(
                section.heading_role
            ),
            paragraph_ordinal=(
                paragraph.ordinal
            ),
            text=(
                paragraph.text
            ),
        )
        for section in document.sections
        for paragraph in section.paragraphs
    )


def build_retrieval_corpus(
        documents: tuple[
            NormalizedDocument,
            ...,
        ],
) -> tuple[
    RetrievalUnit,
    ...
]:
    if not documents:
        raise ValueError(
            "retrieval documents must not be empty"
        )

    units = tuple(
        unit
        for document in documents
        for unit in build_retrieval_units(
            document
        )
    )

    identities: list[
        RetrievalUnitId
    ] = [
        unit.identity
        for unit in units
    ]

    if (
            len(identities)
            != len(set(identities))
    ):
        raise ValueError(
            "retrieval corpus contains "
            "duplicate unit identities"
        )

    return units