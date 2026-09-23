import httpx

from thesis_factory.domain.source import SourceRecord
from thesis_factory.domain.source_text import (
    SourceTextLocationKind,
)
from thesis_factory.integrations.openalex.client import (
    OpenAlexClient,
)


def test_get_text_locations_maps_openalex_full_text_sources() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        assert (
                request.url.path
                == "/works/W123"
        )

        return httpx.Response(
            200,
            json={
                "id": "https://openalex.org/W123",
                "content_urls": {
                    "pdf": (
                        "https://content.openalex.org/"
                        "works/W123.pdf"
                    ),
                    "grobid_xml": (
                        "https://content.openalex.org/"
                        "works/W123.grobid-xml"
                    ),
                },
                "best_oa_location": {
                    "is_oa": True,
                    "landing_page_url": (
                        "https://repository.example/paper"
                    ),
                    "pdf_url": (
                        "https://repository.example/paper.pdf"
                    ),
                    "license": "cc-by",
                    "version": "acceptedVersion",
                    "source": {
                        "display_name": (
                            "Example Repository"
                        ),
                    },
                },
            },
        )

    transport = httpx.MockTransport(
        handler
    )

    with httpx.Client(
            base_url=OpenAlexClient.BASE_URL,
            transport=transport,
    ) as http_client:
        client = OpenAlexClient(
            http_client=http_client,
        )

        locations = client.get_text_locations(
            SourceRecord(
                title="Example",
                provider="openalex",
                provider_id=(
                    "https://openalex.org/W123"
                ),
            )
        )

    assert [
               location.kind
               for location in locations
           ] == [
               SourceTextLocationKind.OPENALEX_GROBID_XML,
               SourceTextLocationKind.OPENALEX_PDF,
               SourceTextLocationKind.ORIGINAL_PDF,
               SourceTextLocationKind.LANDING_PAGE,
           ]

    assert locations[2].host_name == (
        "Example Repository"
    )

    assert locations[2].license == "cc-by"

    assert locations[2].version == (
        "acceptedVersion"
    )

def test_get_text_locations_returns_empty_when_none_available() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "https://openalex.org/W123",
                "content_urls": None,
                "best_oa_location": None,
            },
        )

    transport = httpx.MockTransport(
        handler
    )

    with httpx.Client(
            base_url=OpenAlexClient.BASE_URL,
            transport=transport,
    ) as http_client:
        client = OpenAlexClient(
            http_client=http_client,
        )

        locations = client.get_text_locations(
            SourceRecord(
                title="Example",
                provider="openalex",
                provider_id=(
                    "https://openalex.org/W123"
                ),
            )
        )

    assert locations == ()

def test_get_text_locations_uses_all_open_access_locations() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "https://openalex.org/W123",
                "content_urls": None,
                "best_oa_location": {
                    "is_oa": True,
                    "landing_page_url": (
                        "https://publisher.example/article"
                    ),
                    "pdf_url": None,
                    "license": None,
                    "version": "publishedVersion",
                    "source": {
                        "display_name": "Publisher",
                    },
                },
                "locations": [
                    {
                        "is_oa": True,
                        "landing_page_url": (
                            "https://publisher.example/article"
                        ),
                        "pdf_url": None,
                        "license": None,
                        "version": "publishedVersion",
                        "source": {
                            "display_name": "Publisher",
                        },
                    },
                    {
                        "is_oa": True,
                        "landing_page_url": (
                            "https://repository.example/record"
                        ),
                        "pdf_url": (
                            "https://repository.example/paper.pdf"
                        ),
                        "license": "cc-by",
                        "version": "acceptedVersion",
                        "source": {
                            "display_name": (
                                "University Repository"
                            ),
                        },
                    },
                    {
                        "is_oa": False,
                        "landing_page_url": (
                            "https://closed.example/article"
                        ),
                        "pdf_url": None,
                        "license": None,
                        "version": "publishedVersion",
                        "source": {
                            "display_name": "Closed Publisher",
                        },
                    },
                ],
            },
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(
            base_url=OpenAlexClient.BASE_URL,
            transport=transport,
    ) as http_client:
        client = OpenAlexClient(
            http_client=http_client,
        )

        locations = client.get_text_locations(
            SourceRecord(
                title="Example",
                provider="openalex",
                provider_id=(
                    "https://openalex.org/W123"
                ),
            )
        )

    urls = {
        location.url
        for location in locations
    }

    assert (
            "https://repository.example/paper.pdf"
            in urls
    )

    assert (
            "https://repository.example/record"
            in urls
    )

    assert (
            "https://closed.example/article"
            not in urls
    )

    # best_oa_location also exists inside locations,
    # but it must not be duplicated.
    assert (
            len([
                location
                for location in locations
                if (
                        location.url
                        == "https://publisher.example/article"
                )
            ])
            == 1
    )