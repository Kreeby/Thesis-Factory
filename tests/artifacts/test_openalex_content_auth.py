import httpx
import pytest

from thesis_factory.artifacts.fetching import (
    ArtifactFetchError,
    ArtifactFetcher,
)
from thesis_factory.domain.source_text import (
    SourceTextLocation,
    SourceTextLocationKind,
)


def _location() -> SourceTextLocation:
    return SourceTextLocation(
        kind=(
            SourceTextLocationKind
            .OPENALEX_GROBID_XML
        ),
        url=(
            "https://content.openalex.org/"
            "works/W123.grobid-xml"
        ),
        provider="openalex",
        provider_work_id=(
            "https://openalex.org/W123"
        ),
        is_open_access=True,
    )


def test_openalex_content_fetch_sends_api_key() -> None:
    seen = {}

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        seen["api_key"] = (
            request.url.params.get(
                "api_key"
            )
        )

        return httpx.Response(
            200,
            content=(
                b'<?xml version="1.0"?>'
                b"<TEI><text>"
                b"<p>Evidence</p>"
                b"</text></TEI>"
            ),
        )

    with httpx.Client(
        transport=httpx.MockTransport(
            handler
        ),
    ) as http_client:
        artifact = ArtifactFetcher(
            openalex_api_key="secret-key",
            http_client=http_client,
        ).fetch(
            _location()
        )

    assert seen["api_key"] == "secret-key"
    assert artifact.content_length > 0


def test_openalex_error_never_exposes_api_key() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            401,
            content=b"unauthorized",
        )

    with httpx.Client(
        transport=httpx.MockTransport(
            handler
        ),
    ) as http_client:
        fetcher = ArtifactFetcher(
            openalex_api_key=(
                "super-secret-key"
            ),
            http_client=http_client,
        )

        with pytest.raises(
            ArtifactFetchError,
        ) as captured:
            fetcher.fetch(
                _location()
            )

    message = str(
        captured.value
    )

    assert "super-secret-key" not in message
    assert "api_key" not in message
    assert "401" in message


def test_openalex_content_requires_key() -> None:
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                content=b"unused",
            )
        ),
    ) as http_client:
        fetcher = ArtifactFetcher(
            http_client=http_client,
        )

        with pytest.raises(
            ArtifactFetchError,
            match="requires an API key",
        ):
            fetcher.fetch(
                _location()
            )
