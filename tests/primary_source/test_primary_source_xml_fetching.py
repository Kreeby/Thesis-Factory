import httpx

from thesis_factory.primary_source.fetching import (
    PrimarySourceFetcher,
)


def test_fetcher_normalizes_xml() -> None:
    content = b"""<?xml version="1.0"?>
    <DOC>
      <TI.ART>Article 15</TI.ART>
      <PARAG>
        <P>Meaningful information about the logic involved.</P>
      </PARAG>
      <PARAG>
        <P>The information must be intelligible.</P>
      </PARAG>
    </DOC>
    """

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            request=request,
            content=content,
            headers={
                "content-type": "text/xml",
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
                    "legal-content/EN/TXT/XML/"
                    "?uri=CELEX:62022CJ0203"
                )
            )
        )

    text = " ".join(
        item.text
        for item in document.paragraphs
    )

    assert "Meaningful information" in text
    assert "intelligible" in text


def test_fetcher_retries_502_then_succeeds() -> None:
    calls = 0

    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        nonlocal calls
        calls += 1

        if calls == 1:
            return httpx.Response(
                502,
                request=request,
            )

        return httpx.Response(
            200,
            request=request,
            content=(
                b"<html><body>"
                b"<p>Official text.</p>"
                b"</body></html>"
            ),
            headers={
                "content-type": "text/html",
            },
        )

    with httpx.Client(
        transport=httpx.MockTransport(
            handler
        ),
    ) as http_client:
        document = (
            PrimarySourceFetcher(
                retry_attempts=2,
                retry_backoff_seconds=0,
                sleep_fn=lambda _: None,
                http_client=http_client,
            )
            .fetch(
                url=(
                    "https://eur-lex.europa.eu/test"
                )
            )
        )

    assert calls == 2
    assert document.paragraphs[0].text == (
        "Official text."
    )
