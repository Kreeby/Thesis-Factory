from thesis_factory.domain.document import (
    NormalizedDocument,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceContext,
)
from thesis_factory.domain.retrieval import (
    RetrievalHit,
    RetrievalUnit,
)


class EvidenceContextError(
    ValueError
):
    pass


def expand_retrieval_context(
        document: NormalizedDocument,
        hit: RetrievalHit,
        *,
        neighbours_before: int = 1,
        neighbours_after: int = 1,
        cross_section: bool = False,
) -> EvidenceContext:
    if neighbours_before < 0:
        raise ValueError(
            "neighbours_before must not be negative"
        )

    if neighbours_after < 0:
        raise ValueError(
            "neighbours_after must not be negative"
        )

    _validate_hit_document_identity(
        document,
        hit,
    )

    ordered_units = tuple(
        _document_units(
            document
        )
    )

    hit_index = _find_hit_index(
        ordered_units,
        hit,
    )

    if cross_section:
        lower_bound = max(
            0,
            hit_index - neighbours_before,
        )

        upper_bound = min(
            len(ordered_units),
            hit_index
            + neighbours_after
            + 1,
        )

        context_units = ordered_units[
            lower_bound:
            upper_bound
        ]

    else:
        same_section = tuple(
            unit
            for unit in ordered_units
            if (
                unit.section_ordinal
                == hit.unit.section_ordinal
            )
        )

        section_hit_index = (
            _find_hit_index(
                same_section,
                hit,
            )
        )

        lower_bound = max(
            0,
            section_hit_index
            - neighbours_before,
        )

        upper_bound = min(
            len(same_section),
            section_hit_index
            + neighbours_after
            + 1,
        )

        context_units = same_section[
            lower_bound:
            upper_bound
        ]

    return EvidenceContext(
        hit_identity=hit.unit.identity,
        units=context_units,
    )


def _validate_hit_document_identity(
        document: NormalizedDocument,
        hit: RetrievalHit,
) -> None:
    if (
            hit.unit.artifact_sha256
            != document.artifact_sha256
    ):
        raise EvidenceContextError(
            "retrieval hit targets "
            "a different artifact"
        )

    if (
            hit.unit.normalization_version
            != document.normalization_version
    ):
        raise EvidenceContextError(
            "retrieval hit targets "
            "a different normalization version"
        )


def _document_units(
        document: NormalizedDocument,
):
    for section in document.sections:
        for paragraph in section.paragraphs:
            yield RetrievalUnit(
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


def _find_hit_index(
        units: tuple[
            RetrievalUnit,
            ...,
        ],
        hit: RetrievalHit,
) -> int:
    for index, unit in enumerate(
            units
    ):
        if unit.identity != hit.unit.identity:
            continue

        if unit != hit.unit:
            raise EvidenceContextError(
                "retrieval hit content does not match "
                "the normalized document"
            )

        return index

    raise EvidenceContextError(
        "retrieval hit does not exist "
        "in normalized document"
    )
