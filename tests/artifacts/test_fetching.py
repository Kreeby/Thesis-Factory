import hashlib

import httpx
import pytest

from thesis_factory.artifacts.fetching import (
    ArtifactFetcher,
    ArtifactFormat,
    select_preferred_text_location,
)
from thesis_factory.domain.source_text import (
    SourceTextLocation,
    SourceTextLocationKind,
)


def location(
        kind: SourceTextLocationKind,
        url: str,
) -> SourceTextLocation:
    return SourceTextLocation(
        kind=kind,
        url=url,
        provider="openalex",
        provider_work_id=(
            "https://openalex.org/W123"
        ),
        is_open_access=True,
    )


def test_prefers_grobid_over_pdf() -> None:
    locations = (
        location(
            SourceTextLocationKind.ORIGINAL_PDF,
            "https://example.org/original.pdf",
        ),
        location(
            SourceTextLocationKind.OPENALEX_GROBID_XML,
            "https://example.org/article.xml",
        ),
        location(
            SourceTextLocationKind.OPENALEX_PDF,
            "https://example.org/cached.pdf",
        ),
    )

    result = select_preferred_text_location(
        locations
    )

    assert result is not None

    assert (
            result.kind
            == SourceTextLocationKind.OPENALEX_GROBID_XML
    )


def test_landing_page_is_not_full_text() -> None:
    locations = (
        location(
            SourceTextLocationKind.LANDING_PAGE,
            "https://example.org/article",
        ),
    )

    assert (
            select_preferred_text_location(
                locations
            )
            is None
    )


def test_fetches_pdf_and_records_hash() -> None:
    content = (
        b"%PDF-1.7\n"
        b"example pdf content"
    )

    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            content=content,
            headers={
                "content-type": (
                    "application/pdf"
                )
            },
        )

    transport = httpx.MockTransport(
        handler
    )

    with httpx.Client(
            transport=transport,
    ) as http_client:
        fetcher = ArtifactFetcher(
            http_client=http_client,
        )

        artifact = fetcher.fetch(
            location(
                SourceTextLocationKind.ORIGINAL_PDF,
                "https://example.org/paper.pdf",
            )
        )

    assert (
            artifact.format
            == ArtifactFormat.PDF
    )

    assert artifact.content == content

    assert artifact.sha256 == (
        hashlib.sha256(
            content
        ).hexdigest()
    )

    assert (
            artifact.content_length
            == len(content)
    )


def test_fetches_grobid_xml() -> None:
    content = (
        b'<?xml version="1.0"?>'
        b"<TEI>"
        b"<text>Example</text>"
        b"</TEI>"
    )

    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            content=content,
        )

    transport = httpx.MockTransport(
        handler
    )

    with httpx.Client(
            transport=transport,
    ) as http_client:
        fetcher = ArtifactFetcher(
            http_client=http_client,
        )

        artifact = fetcher.fetch(
            location(
                SourceTextLocationKind.OPENALEX_GROBID_XML,
                "https://example.org/article.xml",
            )
        )

    assert (
            artifact.format
            == ArtifactFormat.GROBID_XML
    )


def test_rejects_html_disguised_as_pdf() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            content=(
                b"<html>"
                b"Access denied"
                b"</html>"
            ),
        )

    transport = httpx.MockTransport(
        handler
    )

    with httpx.Client(
            transport=transport,
    ) as http_client:
        fetcher = ArtifactFetcher(
            http_client=http_client,
        )

        with pytest.raises(
                ValueError,
                match="not a PDF",
        ):
            fetcher.fetch(
                location(
                    SourceTextLocationKind.ORIGINAL_PDF,
                    "https://example.org/paper.pdf",
                )
            )