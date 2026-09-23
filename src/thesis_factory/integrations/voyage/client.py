import math
import time
from collections.abc import Callable
from typing import Literal

import httpx
from pydantic import (
    BaseModel,
    Field,
)


EmbeddingVector = tuple[
    float,
    ...
]


_RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


class _VoyageEmbeddingItem(BaseModel):
    index: int = Field(
        ge=0,
    )

    embedding: tuple[
        float,
        ...,
    ] = Field(
        min_length=1,
    )


class _VoyageEmbeddingResponse(BaseModel):
    data: tuple[
        _VoyageEmbeddingItem,
        ...,
    ]


class VoyageEmbeddingClient:
    BASE_URL = (
        "https://api.voyageai.com"
    )

    def __init__(
            self,
            *,
            api_key: str,
            model: str = "voyage-4",
            batch_size: int = 24,
            max_retries: int = 5,
            retry_base_seconds: float = 1.0,
            min_request_interval_seconds: float = 21.0,
            http_client: httpx.Client | None = None,
            sleeper: Callable[
                [float],
                None,
            ] = time.sleep,
            clock: Callable[
                [],
                float,
            ] = time.monotonic,
    ) -> None:
        normalized_api_key = (
            api_key.strip()
        )

        normalized_model = (
            model.strip()
        )

        if not normalized_api_key:
            raise ValueError(
                "Voyage API key must not be empty"
            )

        if not normalized_model:
            raise ValueError(
                "Voyage model must not be empty"
            )

        if not 1 <= batch_size <= 128:
            raise ValueError(
                "batch_size must be between "
                "1 and 128"
            )

        if max_retries < 0:
            raise ValueError(
                "max_retries must not be negative"
            )

        if retry_base_seconds < 0:
            raise ValueError(
                "retry_base_seconds must not "
                "be negative"
            )

        if (
                min_request_interval_seconds
                < 0
        ):
            raise ValueError(
                "min_request_interval_seconds "
                "must not be negative"
            )

        self._api_key = (
            normalized_api_key
        )

        self._model = (
            normalized_model
        )

        self._batch_size = (
            batch_size
        )

        self._max_retries = (
            max_retries
        )

        self._retry_base_seconds = (
            retry_base_seconds
        )

        self._min_request_interval_seconds = (
            min_request_interval_seconds
        )

        self._sleeper = sleeper
        self._clock = clock

        self._last_request_at: (
                float | None
        ) = None

        self._http_client = (
                http_client
                or httpx.Client(
            base_url=self.BASE_URL,
            timeout=30.0,
        )
        )

        self._owns_http_client = (
                http_client is None
        )

    @property
    def model(
            self,
    ) -> str:
        return self._model

    def embed_documents(
            self,
            texts: tuple[
                str,
                ...,
            ],
    ) -> tuple[
        EmbeddingVector,
        ...
    ]:
        return self._embed(
            texts,
            input_type="document",
        )

    def embed_query(
            self,
            text: str,
    ) -> EmbeddingVector:
        normalized = (
            text.strip()
        )

        if not normalized:
            raise ValueError(
                "embedding query must not be empty"
            )

        embeddings = self._embed(
            (
                normalized,
            ),
            input_type="query",
        )

        return embeddings[0]

    def _embed(
            self,
            texts: tuple[
                str,
                ...,
            ],
            *,
            input_type: Literal[
                "query",
                "document",
            ],
    ) -> tuple[
        EmbeddingVector,
        ...
    ]:
        if not texts:
            raise ValueError(
                "embedding texts must not be empty"
            )

        normalized = tuple(
            text.strip()
            for text in texts
        )

        if any(
                not text
                for text in normalized
        ):
            raise ValueError(
                "embedding texts must not contain "
                "empty values"
            )

        embeddings: list[
            EmbeddingVector
        ] = []

        for start in range(
                0,
                len(normalized),
                self._batch_size,
        ):
            batch = normalized[
                start:
                start + self._batch_size
            ]

            embeddings.extend(
                self._embed_batch(
                    batch,
                    input_type=input_type,
                )
            )

        result = tuple(
            embeddings
        )

        if (
                len(result)
                != len(normalized)
        ):
            raise ValueError(
                "Voyage returned an unexpected "
                "number of embeddings"
            )

        dimensions = {
            len(embedding)
            for embedding in result
        }

        if len(dimensions) != 1:
            raise ValueError(
                "Voyage returned inconsistent "
                "embedding dimensions"
            )

        return result

    def _embed_batch(
            self,
            texts: tuple[
                str,
                ...,
            ],
            *,
            input_type: Literal[
                "query",
                "document",
            ],
    ) -> tuple[
        EmbeddingVector,
        ...
    ]:
        response = (
            self._post_with_retry(
                texts,
                input_type=input_type,
            )
        )

        payload = (
            _VoyageEmbeddingResponse
            .model_validate(
                response.json()
            )
        )

        if (
                len(payload.data)
                != len(texts)
        ):
            raise ValueError(
                "Voyage returned an unexpected "
                "number of embeddings"
            )

        indices = tuple(
            item.index
            for item in payload.data
        )

        if (
                len(indices)
                != len(set(indices))
        ):
            raise ValueError(
                "Voyage returned duplicate "
                "embedding indices"
            )

        expected_indices = set(
            range(
                len(texts)
            )
        )

        if (
                set(indices)
                != expected_indices
        ):
            raise ValueError(
                "Voyage returned invalid "
                "embedding indices"
            )

        ordered = tuple(
            sorted(
                payload.data,
                key=lambda item: (
                    item.index
                ),
            )
        )

        dimensions = {
            len(item.embedding)
            for item in ordered
        }

        if len(dimensions) != 1:
            raise ValueError(
                "Voyage returned inconsistent "
                "embedding dimensions"
            )

        for item in ordered:
            if not all(
                    math.isfinite(value)
                    for value
                    in item.embedding
            ):
                raise ValueError(
                    "Voyage returned a non-finite "
                    "embedding value"
                )

        return tuple(
            item.embedding
            for item in ordered
        )

    def _post_with_retry(
            self,
            texts: tuple[
                str,
                ...,
            ],
            *,
            input_type: Literal[
                "query",
                "document",
            ],
    ) -> httpx.Response:
        attempt = 0

        while True:
            self._wait_for_request_slot()

            self._last_request_at = (
                self._clock()
            )

            response = (
                self._http_client.post(
                    "/v1/embeddings",
                    headers={
                        "Authorization": (
                            f"Bearer "
                            f"{self._api_key}"
                        ),
                        "Content-Type": (
                            "application/json"
                        ),
                    },
                    json={
                        "input": list(
                            texts
                        ),
                        "model": self._model,
                        "input_type": (
                            input_type
                        ),
                        "truncation": False,
                        "output_dtype": (
                            "float"
                        ),
                    },
                )
            )

            if (
                    response.status_code
                    not in _RETRYABLE_STATUS_CODES
            ):
                response.raise_for_status()

                return response

            if (
                    attempt
                    >= self._max_retries
            ):
                response.raise_for_status()

            delay = (
                self._retry_delay(
                    response,
                    attempt=attempt,
                )
            )

            self._sleeper(
                delay
            )

            attempt += 1

    def _wait_for_request_slot(
            self,
    ) -> None:
        if (
                self._last_request_at
                is None
        ):
            return

        if (
                self._min_request_interval_seconds
                == 0
        ):
            return

        elapsed = (
                self._clock()
                - self._last_request_at
        )

        remaining = (
                self._min_request_interval_seconds
                - elapsed
        )

        if remaining > 0:
            self._sleeper(
                remaining
            )

    def _retry_delay(
            self,
            response: httpx.Response,
            *,
            attempt: int,
    ) -> float:
        retry_after = (
            response.headers.get(
                "Retry-After"
            )
        )

        if retry_after is not None:
            try:
                parsed = float(
                    retry_after
                )

                if parsed >= 0:
                    return parsed

            except ValueError:
                pass

        exponential = (
                self._retry_base_seconds
                * (
                        2 ** attempt
                )
        )

        return min(
            exponential,
            30.0,
        )

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()