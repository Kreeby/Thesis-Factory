from thesis_factory.domain.source_text import (
    SourceTextLocation,
    SourceTextLocationKind,
)


def test_source_text_location_is_immutable() -> None:
    location = SourceTextLocation(
        kind=SourceTextLocationKind.ORIGINAL_PDF,
        url="https://example.org/paper.pdf",
        provider="openalex",
        provider_work_id="https://openalex.org/W123",
        is_open_access=True,
    )

    assert (
            location.kind
            == SourceTextLocationKind.ORIGINAL_PDF
    )