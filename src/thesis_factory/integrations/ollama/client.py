from typing import TypeVar

import httpx
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class OllamaStructuredReasoner:
    """Local structured reasoner; output is constrained to the model's JSON schema."""

    def __init__(
            self,
            *,
            model: str,
            base_url: str = "http://localhost:11434",
            timeout_seconds: float = 300.0,
            http_client: httpx.Client | None = None,
    ) -> None:
        normalized_model = model.strip()

        if not normalized_model:
            raise ValueError(
                "Ollama model must not be empty"
            )

        self._model = normalized_model
        self._client = http_client or httpx.Client(
            base_url=base_url,
            timeout=timeout_seconds,
        )

    def generate(
            self,
            *,
            system: str,
            prompt: str,
            output_model: type[T],
    ) -> T:
        response = self._client.post(
            "/api/chat",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "format": output_model.model_json_schema(),
                "stream": False,
                "think": False,
                "options": {"temperature": 0},
            },
        )
        response.raise_for_status()
        payload = response.json()

        # Truncated JSON must fail loudly, never be partially parsed.
        if payload.get("done_reason") == "length":
            raise RuntimeError(
                "Ollama output was truncated at the token limit"
            )

        return output_model.model_validate_json(
            payload["message"]["content"]
        )
