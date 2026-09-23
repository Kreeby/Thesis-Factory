import httpx

from thesis_factory.integrations.openalex.client import OpenAlexClient


def test_search_works_maps_openalex_response_to_source_records() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/works"
        assert request.url.params["search"] == "credit risk machine learning"
        assert request.url.params["per_page"] == "2"

        return httpx.Response(
            200,
            json={
                "meta": {
                    "count": 1,
                    "page": 1,
                    "per_page": 2,
                },
                "results": [
                    {
                        "id": "https://openalex.org/W123456",
                        "doi": "https://doi.org/10.1234/example",
                        "title": "Machine Learning for Credit Risk",
                        "publication_year": 2025,
                        "authorships": [
                            {
                                "author": {
                                    "display_name": "Alice Smith",
                                }
                            },
                            {
                                "author": {
                                    "display_name": "Bob Jones",
                                }
                            },
                        ],
                        "primary_location": {
                            "source": {
                                "display_name": "Journal of Example Finance",
                            }
                        },
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(
            base_url=OpenAlexClient.BASE_URL,
            transport=transport,
    ) as http_client:
        client = OpenAlexClient(http_client=http_client)

        sources = client.search_works(
            "credit risk machine learning",
            per_page=2,
        )

    assert len(sources) == 1

    source = sources[0]

    assert source.provider == "openalex"
    assert source.provider_id == "https://openalex.org/W123456"
    assert source.title == "Machine Learning for Credit Risk"
    assert source.authors == ("Alice Smith", "Bob Jones")
    assert source.publication_year == 2025
    assert source.doi == "10.1234/example"
    assert source.venue == "Journal of Example Finance"