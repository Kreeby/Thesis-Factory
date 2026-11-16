from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from thesis_factory.integrations.anthropic.client import (
    AnthropicStructuredReasoner,
)


class _Answer(BaseModel):
    status: str


def _reasoner(text: str, stop_reason: str):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            stop_reason=stop_reason,
            content=[SimpleNamespace(type="text", text=text)],
        )

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    reasoner = AnthropicStructuredReasoner(
        model="claude-test",
        client=client,
        max_tokens=64,
    )
    return reasoner, calls


def test_returns_validated_output_with_schema_format() -> None:
    reasoner, calls = _reasoner('{"status": "PASS"}', "end_turn")

    result = reasoner.generate(
        system="sys",
        prompt="prompt",
        output_model=_Answer,
    )

    assert result == _Answer(status="PASS")
    assert calls[0]["output_config"]["format"]["type"] == "json_schema"


def test_truncated_output_raises_explicit_error() -> None:
    reasoner, _ = _reasoner('{"status": "PA', "max_tokens")

    with pytest.raises(RuntimeError, match="truncated at max_tokens=64"):
        reasoner.generate(
            system="sys",
            prompt="prompt",
            output_model=_Answer,
        )
