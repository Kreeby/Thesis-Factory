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
