from typing import TypeVar

from anthropic import Anthropic, transform_schema
from pydantic import BaseModel

from thesis_factory.integrations.anthropic.client_factory import (
    create_anthropic_client,
)


T = TypeVar("T", bound=BaseModel)


class AnthropicStructuredReasoner:
    def __init__(
            self,
            *,
            model: str,
            client: Anthropic | None = None,
            max_tokens: int = 512,
    ) -> None:
        self._model = model
        self._client = (
            client
            or create_anthropic_client()
        )
        self._max_tokens = max_tokens

    def generate(
            self,
            *,
            system: str,
            prompt: str,
            output_model: type[T],
    ) -> T:
        # create() instead of parse(): parse() validates before stop_reason
        # can be inspected, hiding truncation behind a generic EOF error.
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": transform_schema(
                        output_model.model_json_schema()
                    ),
                },
            },
        )

        if response.stop_reason == "max_tokens":
            raise RuntimeError(
                "Claude output was truncated at max_tokens="
                f"{self._max_tokens}"
            )

        text = "".join(
            block.text
            for block in response.content
            if block.type == "text"
        )

        if not text.strip():
            raise RuntimeError(
                "Claude returned no structured output"
            )

        return output_model.model_validate_json(text)
