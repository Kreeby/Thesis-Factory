from typing import TypeVar

from anthropic import Anthropic
from pydantic import BaseModel


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
        self._client = client or Anthropic()
        self._max_tokens = max_tokens

    def generate(
            self,
            *,
            system: str,
            prompt: str,
            output_model: type[T],
    ) -> T:
        response = self._client.messages.parse(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            output_format=output_model,
        )

        result = response.parsed_output

        if result is None:
            raise RuntimeError(
                "Claude returned no structured output"
            )

        return result