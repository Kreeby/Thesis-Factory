import httpx

from thesis_factory.primary_source.fetching import (
    PrimarySourceFetcher,
)


def test_cellar_fetch_uses_content_negotiation_headers() -> None:
    seen = {}

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        seen["accept"] = (
            request.headers.get(
                "accept"
            )
        )
        seen["language"] = (
            request.headers.get(
                "accept-language"
            )
        )

        return httpx.Response(
            200,
            request=request,
            content=(
                b"<html><body>"
                b"<p>Official judgment text.</p>"
                b"</body></html>"
            ),
            headers={
                "content-type": (
                    "application/xhtml+xml"
                ),
            },
        )

    with httpx.Client(
        transport=httpx.MockTransport(
            handler
        ),
    ) as http_client:
        document = (
            PrimarySourceFetcher(
                http_client=http_client,
            )
            .fetch(
                url=(
                    "https://publications.europa.eu/"
                    "resource/celex/62021CJ0634"
                    "?language=eng"
                )
            )
        )

    assert (
        "application/xhtml+xml"
        in seen["accept"]
    )
    assert seen["language"] == "eng"
    assert (
        document.paragraphs[0].text
        == "Official judgment text."
    )
