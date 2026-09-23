import httpx

from thesis_factory.integrations.crossref.client import CrossrefClient


def test_get_work_by_doi_maps_crossref_metadata() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.startswith("/works/")

        return httpx.Response(
            200,
            json={
                "status": "ok",
                "message-type": "work",
                "message": {
                    "DOI": "10.1234/example",
                    "title": [
                        "Machine Learning for Credit Risk"
                    ],
                    "author": [
                        {
                            "given": "Alice",
                            "family": "Smith",
                        },
                        {
                            "given": "Bob",
                            "family": "Jones",
                        },
                    ],
                    "container-title": [
                        "Journal of Example Finance"
                    ],
                    "published-print": {
                        "date-parts": [[2025, 6, 1]]
                    },
                },
            },
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(
            base_url=CrossrefClient.BASE_URL,
            transport=transport,
    ) as http_client:
        client = CrossrefClient(http_client=http_client)

        source = client.get_work_by_doi(
            "10.1234/example"
        )

    assert source is not None
    assert source.provider == "crossref"
    assert source.provider_id == "10.1234/example"
    assert source.title == "Machine Learning for Credit Risk"
    assert source.authors == ("Alice Smith", "Bob Jones")
    assert source.publication_year == 2025
    assert source.doi == "10.1234/example"
    assert source.venue == "Journal of Example Finance"


def test_get_work_by_doi_returns_none_for_unknown_doi() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    with httpx.Client(
            base_url=CrossrefClient.BASE_URL,
            transport=transport,
    ) as http_client:
        client = CrossrefClient(http_client=http_client)

        source = client.get_work_by_doi(
            "10.1234/does-not-exist"
        )

    assert source is None