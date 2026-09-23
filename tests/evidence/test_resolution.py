import pytest
from pydantic import (
    ValidationError,
)

from thesis_factory.domain.document import (
    DocumentSectionKind,
    NormalizedDocument,
    NormalizedParagraph,
    NormalizedSection,
)
from thesis_factory.domain.evidence import (
    EvidenceAddress,
)
from thesis_factory.evidence.resolution import (
    EvidenceResolutionError,
    resolve_evidence_span,
    verify_evidence_span,
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
                        text=(
                            "This paper studies "
                            "credit risk."
                        ),
                    ),
                ),
            ),
            NormalizedSection(
                ordinal=2,
                kind=(
                    DocumentSectionKind
                    .BODY
                ),
                path=(
                    "Machine Learning Models",
                ),
                paragraphs=(
                    NormalizedParagraph(
                        ordinal=2,
                        text=(
                            "Models use machine learning "
                            "for credit risk prediction."
                        ),
                    ),
                ),
            ),
        ),
    )


def test_resolves_exact_text_span() -> None:
    document = _document()

    address = EvidenceAddress(
        artifact_sha256=SHA256,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=2,
        start_char=11,
        end_char=27,
    )

    evidence = resolve_evidence_span(
        document,
        address,
    )

    assert (
            evidence.text
            == "machine learning"
    )

    assert (
            evidence.section_ordinal
            == 2
    )

    assert evidence.section_path == (
        "Machine Learning Models",
    )

    assert (
            evidence.source_provider
            == "openalex"
    )


def test_rejects_wrong_artifact() -> None:
    document = _document()

    address = EvidenceAddress(
        artifact_sha256="b" * 64,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=2,
        start_char=0,
        end_char=6,
    )

    with pytest.raises(
            EvidenceResolutionError,
            match="different artifact",
    ):
        resolve_evidence_span(
            document,
            address,
        )


def test_rejects_wrong_normalization_version() -> None:
    document = _document()

    address = EvidenceAddress(
        artifact_sha256=SHA256,
        normalization_version=(
            "some-future-normalizer"
        ),
        paragraph_ordinal=2,
        start_char=0,
        end_char=6,
    )

    with pytest.raises(
            EvidenceResolutionError,
            match=(
                    "different normalization version"
            ),
    ):
        resolve_evidence_span(
            document,
            address,
        )


def test_rejects_missing_paragraph() -> None:
    document = _document()

    address = EvidenceAddress(
        artifact_sha256=SHA256,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=999,
        start_char=0,
        end_char=1,
    )

    with pytest.raises(
            EvidenceResolutionError,
            match="paragraph ordinal",
    ):
        resolve_evidence_span(
            document,
            address,
        )


def test_rejects_out_of_bounds_character_range() -> None:
    document = _document()

    address = EvidenceAddress(
        artifact_sha256=SHA256,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=2,
        start_char=0,
        end_char=999,
    )

    with pytest.raises(
            EvidenceResolutionError,
            match="paragraph length",
    ):
        resolve_evidence_span(
            document,
            address,
        )


def test_verifies_untampered_evidence() -> None:
    document = _document()

    address = EvidenceAddress(
        artifact_sha256=SHA256,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=2,
        start_char=11,
        end_char=27,
    )

    evidence = resolve_evidence_span(
        document,
        address,
    )

    verify_evidence_span(
        document,
        evidence,
    )


def test_rejects_tampered_evidence_text() -> None:
    document = _document()

    address = EvidenceAddress(
        artifact_sha256=SHA256,
        normalization_version=(
            "grobid-tei-v1"
        ),
        paragraph_ordinal=2,
        start_char=11,
        end_char=27,
    )

    evidence = resolve_evidence_span(
        document,
        address,
    )

    tampered = evidence.model_copy(
        update={
            "text": (
                "machine learning "
                "definitely wins"
            )
        }
    )

    with pytest.raises(
            EvidenceResolutionError,
            match="does not match",
    ):
        verify_evidence_span(
            document,
            tampered,
        )


def test_document_rejects_duplicate_paragraph_ordinals() -> None:
    with pytest.raises(
            ValidationError,
            match=(
                    "paragraph ordinals must be unique"
            ),
    ):
        NormalizedDocument(
            artifact_sha256=SHA256,
            source_provider="openalex",
            source_provider_id=(
                "https://openalex.org/W123"
            ),
            sections=(
                NormalizedSection(
                    ordinal=1,
                    kind=(
                        DocumentSectionKind.BODY
                    ),
                    path=("One",),
                    paragraphs=(
                        NormalizedParagraph(
                            ordinal=1,
                            text="First.",
                        ),
                    ),
                ),
                NormalizedSection(
                    ordinal=2,
                    kind=(
                        DocumentSectionKind.BODY
                    ),
                    path=("Two",),
                    paragraphs=(
                        NormalizedParagraph(
                            ordinal=1,
                            text="Second.",
                        ),
                    ),
                ),
            ),
        )


def test_document_rejects_duplicate_section_ordinals() -> None:
    with pytest.raises(
            ValidationError,
            match=(
                    "section ordinals must be unique"
            ),
    ):
        NormalizedDocument(
            artifact_sha256=SHA256,
            source_provider="openalex",
            source_provider_id=(
                "https://openalex.org/W123"
            ),
            sections=(
                NormalizedSection(
                    ordinal=1,
                    kind=(
                        DocumentSectionKind.BODY
                    ),
                    path=("One",),
                    paragraphs=(
                        NormalizedParagraph(
                            ordinal=1,
                            text="First.",
                        ),
                    ),
                ),
                NormalizedSection(
                    ordinal=1,
                    kind=(
                        DocumentSectionKind.BODY
                    ),
                    path=("Two",),
                    paragraphs=(
                        NormalizedParagraph(
                            ordinal=2,
                            text="Second.",
                        ),
                    ),
                ),
            ),
        )