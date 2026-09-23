import httpx
import pytest

from thesis_factory.integrations.voyage.client import (
    VoyageEmbeddingClient,
)


def _client(
        handler,
        *,
        batch_size: int = 64,
        max_retries: int = 5,
        sleeper=lambda _: None,
        clock=lambda: 0.0,
        min_request_interval_seconds: float = 0.0,
) -> VoyageEmbeddingClient:
    transport = httpx.MockTransport(
        handler
    )

    http_client = httpx.Client(
        base_url=(
            "https://api.voyageai.com"
        ),
        transport=transport,
    )

    return VoyageEmbeddingClient(
        api_key="secret",
        batch_size=batch_size,
        max_retries=max_retries,
        retry_base_seconds=1.0,
        min_request_interval_seconds=(
            min_request_interval_seconds
        ),
        http_client=http_client,
        sleeper=sleeper,
        clock=clock,
    )

def test_embeds_documents_with_document_input_type() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        payload = request.read()

        assert (
                request.headers[
                    "Authorization"
                ]
                == "Bearer secret"
        )

        assert (
                b'"input_type":"document"'
                in payload
        )

        assert (
                b'"truncation":false'
                in payload
        )

        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "index": 0,
                        "embedding": [
                            1.0,
                            0.0,
                        ],
                    },
                    {
                        "index": 1,
                        "embedding": [
                            0.0,
                            1.0,
                        ],
                    },
                ]
            },
        )

    client = _client(
        handler
    )

    embeddings = (
        client.embed_documents(
            (
                "first",
                "second",
            )
        )
    )

    assert embeddings == (
        (
            1.0,
            0.0,
        ),
        (
            0.0,
            1.0,
        ),
    )


def test_embeds_query_with_query_input_type() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        assert (
                b'"input_type":"query"'
                in request.read()
        )

        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "index": 0,
                        "embedding": [
                            0.5,
                            0.5,
                        ],
                    }
                ]
            },
        )

    client = _client(
        handler
    )

    assert client.embed_query(
        "credit risk"
    ) == (
               0.5,
               0.5,
           )


def test_restores_embedding_order_by_index() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "index": 1,
                        "embedding": [
                            0.0,
                            1.0,
                        ],
                    },
                    {
                        "index": 0,
                        "embedding": [
                            1.0,
                            0.0,
                        ],
                    },
                ]
            },
        )

    client = _client(
        handler
    )

    embeddings = (
        client.embed_documents(
            (
                "first",
                "second",
            )
        )
    )

    assert embeddings[0] == (
        1.0,
        0.0,
    )

    assert embeddings[1] == (
        0.0,
        1.0,
    )


def test_batches_large_document_sets() -> None:
    requests = []

    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        requests.append(
            request
        )

        import json

        payload = json.loads(
            request.content
        )

        inputs = payload[
            "input"
        ]

        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "index": index,
                        "embedding": [
                            float(index + 1),
                            1.0,
                        ],
                    }
                    for index, _
                    in enumerate(inputs)
                ]
            },
        )

    client = _client(
        handler,
        batch_size=2,
    )

    result = client.embed_documents(
        (
            "one",
            "two",
            "three",
            "four",
            "five",
        )
    )

    assert len(result) == 5

    assert len(requests) == 3


def test_retries_rate_limit_response() -> None:
    call_count = 0

    waits = []

    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        nonlocal call_count

        call_count += 1

        if call_count == 1:
            return httpx.Response(
                429,
                headers={
                    "Retry-After": "2",
                },
                json={
                    "detail": (
                        "rate limit exceeded"
                    )
                },
            )

        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "index": 0,
                        "embedding": [
                            1.0,
                            0.0,
                        ],
                    }
                ]
            },
        )

    client = _client(
        handler,
        sleeper=waits.append,
    )

    result = (
        client.embed_documents(
            (
                "credit",
            )
        )
    )

    assert result == (
        (
            1.0,
            0.0,
        ),
    )

    assert call_count == 2

    assert waits == [
        2.0,
    ]


def test_stops_after_bounded_retries() -> None:
    call_count = 0

    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        nonlocal call_count

        call_count += 1

        return httpx.Response(
            429,
            json={
                "detail": (
                    "rate limit exceeded"
                )
            },
        )

    client = _client(
        handler,
        max_retries=2,
    )

    with pytest.raises(
            httpx.HTTPStatusError,
    ):
        client.embed_documents(
            (
                "credit",
            )
        )

    assert call_count == 3


def test_rejects_wrong_embedding_count() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "index": 0,
                        "embedding": [
                            1.0,
                        ],
                    }
                ]
            },
        )

    client = _client(
        handler
    )

    with pytest.raises(
            ValueError,
            match="unexpected number",
    ):
        client.embed_documents(
            (
                "first",
                "second",
            )
        )


def test_rejects_inconsistent_dimensions() -> None:
    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "index": 0,
                        "embedding": [
                            1.0,
                        ],
                    },
                    {
                        "index": 1,
                        "embedding": [
                            1.0,
                            2.0,
                        ],
                    },
                ]
            },
        )

    client = _client(
        handler
    )

    with pytest.raises(
            ValueError,
            match="inconsistent",
    ):
        client.embed_documents(
            (
                "first",
                "second",
            )
        )


def test_paces_requests() -> None:
    now = 0.0
    waits = []

    def clock() -> float:
        return now

    def sleep(
            seconds: float,
    ) -> None:
        nonlocal now

        waits.append(
            seconds
        )

        now += seconds

    def handler(
            request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "index": 0,
                        "embedding": [
                            1.0,
                            0.0,
                        ],
                    }
                ]
            },
        )

    client = _client(
        handler,
        batch_size=1,
        min_request_interval_seconds=21.0,
        sleeper=sleep,
        clock=clock,
    )

    client.embed_documents(
        (
            "first",
            "second",
        )
    )

    assert waits == [
        21.0,
    ]