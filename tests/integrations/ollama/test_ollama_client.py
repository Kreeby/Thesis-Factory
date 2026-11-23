import json

import httpx
import pytest
from pydantic import BaseModel, ValidationError

from thesis_factory.integrations.ollama.client import (
    OllamaStructuredReasoner,
)


class _Answer(BaseModel):
    status: str


def _reasoner(handler) -> OllamaStructuredReasoner:
    return OllamaStructuredReasoner(
        model="qwen3:8b",
        http_client=httpx.Client(
            base_url="http://ollama.test",
            transport=httpx.MockTransport(handler),
        ),
    )


def _reply(content: str, done_reason: str = "stop"):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "message": {"content": content},
                "done_reason": done_reason,
            },
        )

    return handler


def test_sends_schema_constrained_deterministic_request() -> None:
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(json.loads(request.content))
        return _reply('{"status": "RELEVANT"}')(request)

    result = _reasoner(handler).generate(
        system="sys",
        prompt="prompt",
        output_model=_Answer,
    )

    assert result == _Answer(status="RELEVANT")
    assert seen["format"] == _Answer.model_json_schema()
    assert seen["options"]["temperature"] == 0
    assert seen["stream"] is False


def test_rejects_truncated_output() -> None:
    with pytest.raises(RuntimeError, match="truncated"):
        _reasoner(_reply('{"status": "REL', "length")).generate(
            system="sys",
            prompt="prompt",
            output_model=_Answer,
        )


def test_rejects_output_violating_schema() -> None:
    with pytest.raises(ValidationError):
        _reasoner(_reply('{"other": 1}')).generate(
            system="sys",
            prompt="prompt",
            output_model=_Answer,
        )


def test_rejects_empty_model() -> None:
    with pytest.raises(ValueError):
        OllamaStructuredReasoner(model="  ")


def test_embedder_batches_and_checks_counts() -> None:
    from thesis_factory.integrations.ollama.client import OllamaEmbedder

    batches = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        batches.append(body["input"])
        assert body["truncate"] is False
        return httpx.Response(200, json={"embeddings": [[float(len(t))] for t in body["input"]]})

    embedder = OllamaEmbedder(
        model="qwen3-embedding:0.6b", batch_size=2,
        http_client=httpx.Client(base_url="http://ollama.test", transport=httpx.MockTransport(handler)),
    )
    assert embedder.embed(["a", "bb", "ccc"]) == [[1.0], [2.0], [3.0]]
    assert batches == [["a", "bb"], ["ccc"]]


def test_embedder_rejects_missing_embeddings() -> None:
    from thesis_factory.integrations.ollama.client import OllamaEmbedder

    embedder = OllamaEmbedder(
        model="m",
        http_client=httpx.Client(
            base_url="http://ollama.test",
            transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"embeddings": []})),
        ),
    )
    with pytest.raises(RuntimeError, match="0 embeddings for 1"):
        embedder.embed(["a"])
