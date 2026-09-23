import httpx
import pytest

from thesis_factory.integrations.openalex.client import (
    OpenAlexClient,
    OpenAlexSearchMode,
)


def _response() -> dict[str, object]:
    return {
        "results": [
            {
                "id": "https://openalex.org/W1",
                "doi": "https://doi.org/10.1234/example",
                "title": "Example Paper",
                "publication_year": 2025,
                "authorships": [],
                "primary_location": None,
                "abstract_inverted_index": None,
            }
        ]
    }


def test_semantic_mode_uses_semantic_search_parameter() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        assert (
                request.url.params.get("search.semantic")
                == "machine learning credit risk"
        )

        assert (
                request.url.params.get("search")
                is None
        )

        return httpx.Response(
            200,
            json=_response(),
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(
            base_url=OpenAlexClient.BASE_URL,
            transport=transport,
    ) as http_client:
        client = OpenAlexClient(
            search_mode=OpenAlexSearchMode.SEMANTIC,
            semantic_min_interval_seconds=0,
            http_client=http_client,
        )

        client.search_works(
            "machine learning credit risk",
            per_page=3,
        )


def test_lexical_mode_uses_lexical_search_parameter() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        assert (
                request.url.params.get("search")
                == "machine learning credit risk"
        )

        assert (
                request.url.params.get("search.semantic")
                is None
        )

        return httpx.Response(
            200,
            json=_response(),
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(
            base_url=OpenAlexClient.BASE_URL,
            transport=transport,
    ) as http_client:
        client = OpenAlexClient(
            http_client=http_client,
        )

        client.search_works(
            "machine learning credit risk",
            per_page=3,
        )


def test_semantic_search_rejects_more_than_fifty_results() -> None:
    client = OpenAlexClient(
        search_mode=OpenAlexSearchMode.SEMANTIC,
    )

    try:
        with pytest.raises(
                ValueError,
                match="per_page must be between 1 and 50",
        ):
            client.search_works(
                "machine learning credit risk",
                per_page=51,
            )
    finally:
        client.close()