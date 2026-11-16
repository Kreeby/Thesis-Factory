import json

import httpx
import pytest

from thesis_factory.integrations.semantic_scholar.client import (
    SemanticScholarClient,
    SemanticScholarError,
)


def _client(handler, *, max_retries=3, sleeps=None, api_key=None):
    sleeps = sleeps if sleeps is not None else []
    headers = {"x-api-key": api_key} if api_key else {}
    return SemanticScholarClient(
        max_retries=max_retries,
        http_client=httpx.Client(
            base_url="https://s2.test",
            transport=httpx.MockTransport(handler),
            headers=headers,
        ),
        sleeper=sleeps.append,
        clock=lambda: 0.0,
    )


def test_bulk_search_follows_continuation_tokens() -> None:
    tokens = []

    def handler(request: httpx.Request) -> httpx.Response:
        token = request.url.params.get("token")
        tokens.append(token)
        if token is None:
            return httpx.Response(
                200, json={"total": 3, "token": "t2", "data": [{"paperId": "a"}]}
            )
        return httpx.Response(
            200, json={"total": 3, "data": [{"paperId": "b"}, {"paperId": "c"}]}
        )

    pages = list(_client(handler).search_bulk_pages("credit"))

    assert [len(p[0]) for p in pages] == [1, 2]
    assert [p[1] for p in pages] == ["t2", None]
    assert tokens == [None, "t2"]



def test_retries_rate_limit_with_bounded_backoff() -> None:
    responses = iter([429, 503, 200])
    sleeps = []

    def handler(request: httpx.Request) -> httpx.Response:
        status = next(responses)
        return httpx.Response(status, json={"total": 0, "data": []})

    list(_client(handler, sleeps=sleeps).search_bulk_pages("q"))

    # Pacing sleeps are skipped by the frozen clock; only backoff remains.
    assert [s for s in sleeps if s >= 2.0] == [2.0, 4.0]


def test_gives_up_after_max_retries() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={})

    with pytest.raises(SemanticScholarError, match="after 3 attempts"):
        list(_client(handler, max_retries=2).search_bulk_pages("q"))



def test_batch_chunks_ids_and_preserves_unknown_entries() -> None:
    sizes = []

    def handler(request: httpx.Request) -> httpx.Response:
        ids = json.loads(request.content)["ids"]
        sizes.append(len(ids))
        return httpx.Response(
            200, json=[None if i == "missing" else {"paperId": i} for i in ids]
        )

    ids = [f"p{i}" for i in range(501)] + ["missing"]
    result = _client(handler).batch(ids, fields="title")

    assert sizes == [500, 2]
    assert result[-1] is None
    assert result[0] == {"paperId": "p0"}

