import time
from collections.abc import Callable, Iterator
from typing import Any

import httpx


_RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}

PAPER_FIELDS = (
    "paperId,externalIds,title,abstract,year,venue,"
    "citationCount,referenceCount,fieldsOfStudy,"
    "publicationTypes,openAccessPdf,authors"
)


class SemanticScholarError(RuntimeError):
    pass


class SemanticScholarClient:
    BASE_URL = "https://api.semanticscholar.org"

    # Documented batch endpoint limit.
    MAX_BATCH_IDS = 500

    def __init__(
            self,
            *,
            api_key: str | None = None,
            max_retries: int = 8,
            retry_base_seconds: float = 2.0,
            max_retry_seconds: float = 60.0,
            min_request_interval_seconds: float = 1.1,
            http_client: httpx.Client | None = None,
            sleeper: Callable[[float], None] = time.sleep,
            clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if max_retries < 0:
            raise ValueError(
                "max_retries must not be negative"
            )

        headers = {}

        if api_key and api_key.strip():
            headers["x-api-key"] = api_key.strip()

        self._max_retries = max_retries
        self._retry_base_seconds = retry_base_seconds
        self._max_retry_seconds = max_retry_seconds
        self._min_interval = min_request_interval_seconds
        self._sleeper = sleeper
        self._clock = clock
        self._last_request_at: float | None = None
        self._http_client = http_client or httpx.Client(
            base_url=self.BASE_URL,
            timeout=60.0,
            headers=headers,
        )

    def search_bulk_pages(
            self,
            query: str,
            *,
            token: str | None = None,
            year: str | None = None,
            fields: str = PAPER_FIELDS,
    ) -> Iterator[tuple[list[dict[str, Any]], str | None, int]]:
        """Yield (papers, next_token, total) pages; resumable from ``token``."""

        if not query.strip():
            raise ValueError("query must not be empty")

        while True:
            params = {"query": query, "fields": fields}

            if token:
                params["token"] = token

            if year:
                params["year"] = year

            payload = self._request(
                "GET",
                "/graph/v1/paper/search/bulk",
                params=params,
            )

            token = payload.get("token")

            yield (
                payload.get("data") or [],
                token,
                int(payload.get("total") or 0),
            )

            if not token:
                return

    def batch(
            self,
            ids: list[str],
            *,
            fields: str,
    ) -> list[dict[str, Any] | None]:
        """Return one entry per id, ``None`` for ids S2 does not know."""

        results: list[dict[str, Any] | None] = []

        for start in range(0, len(ids), self.MAX_BATCH_IDS):
            chunk = ids[start:start + self.MAX_BATCH_IDS]
            payload = self._request(
                "POST",
                "/graph/v1/paper/batch",
                params={"fields": fields},
                json={"ids": chunk},
            )

            if not isinstance(payload, list) or len(payload) != len(chunk):
                raise SemanticScholarError(
                    "batch response does not match requested ids"
                )

            results.extend(payload)

        return results

    def _request(
            self,
            method: str,
            path: str,
            **kwargs: Any,
    ) -> Any:
        attempt = 0

        while True:
            self._wait_for_slot()

            try:
                response = self._http_client.request(
                    method,
                    path,
                    **kwargs,
                )
                retryable = (
                    response.status_code
                    in _RETRYABLE_STATUS_CODES
                )
            except httpx.TransportError as error:
                response = None
                retryable = True
                failure = str(error)

            if response is not None and not retryable:
                if response.status_code >= 400:
                    raise SemanticScholarError(
                        f"{method} {path} failed with HTTP "
                        f"{response.status_code}: "
                        f"{response.text[:200]}"
                    )

                return response.json()

            if response is not None:
                failure = f"HTTP {response.status_code}"

            if attempt >= self._max_retries:
                raise SemanticScholarError(
                    f"{method} {path} failed after "
                    f"{attempt + 1} attempts: {failure}"
                )

            self._sleeper(
                min(
                    self._retry_base_seconds * 2 ** attempt,
                    self._max_retry_seconds,
                )
            )
            attempt += 1

    def _wait_for_slot(self) -> None:
        now = self._clock()

        if self._last_request_at is not None:
            remaining = (
                self._min_interval
                - (now - self._last_request_at)
            )

            if remaining > 0:
                self._sleeper(remaining)

        self._last_request_at = self._clock()
