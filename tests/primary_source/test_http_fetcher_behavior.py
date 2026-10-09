import hashlib

import httpx

from thesis_factory.primary_source.fetching import (
    PrimarySourceFetcher,
)


def test_fetcher_normalizes_html_and_hashes_raw_bytes() -> None:
    content = b"""
    <html>
      <body>
        <script>ignore me</script>
        <h1>Directive 2023/2225</h1>
        <p>Main variable one.</p>
        <p>Main variable two.</p>
      </body>
    </html>
    """

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            request=request,
            content=content,
            headers={
                "content-type": (
                    "text/html; charset=utf-8"
                )
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
                    "https://eur-lex.europa.eu/"
                    "example"
                ),
                title="Directive",
            )
        )

    assert (
        document.artifact_sha256
        == hashlib.sha256(
            content
        ).hexdigest()
    )

    text = " ".join(
        paragraph.text
        for paragraph
        in document.paragraphs
    )

    assert "Main variable one." in text
    assert "ignore me" not in text
