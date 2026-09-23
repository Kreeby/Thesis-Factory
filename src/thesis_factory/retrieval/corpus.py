from thesis_factory.domain.document import (
    NormalizedDocument,
)
from thesis_factory.domain.retrieval import (
    RetrievalUnit,
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