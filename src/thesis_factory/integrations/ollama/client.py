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
            num_ctx: int | None = None,
            http_client: httpx.Client | None = None,
    ) -> None:
        normalized_model = model.strip()

        if not normalized_model:
            raise ValueError(
                "Ollama model must not be empty"
            )

        self._model = normalized_model
        # Ollama silently drops the start of prompts longer than the context window.
        self._num_ctx = num_ctx
        self._options = {"temperature": 0, **({"num_ctx": num_ctx} if num_ctx else {})}
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
                "options": self._options,
            },
        )
        response.raise_for_status()
        payload = response.json()

        # Truncated JSON must fail loudly, never be partially parsed.
        if payload.get("done_reason") == "length":
            raise RuntimeError(
                "Ollama output was truncated at the token limit"
            )

        if self._num_ctx and payload.get("prompt_eval_count", 0) >= self._num_ctx - 16:
            raise RuntimeError(
                "Ollama prompt filled the context window and was likely truncated"
            )

        return output_model.model_validate_json(
            payload["message"]["content"]
        )
