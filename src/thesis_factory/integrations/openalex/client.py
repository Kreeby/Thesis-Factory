from collections.abc import Mapping
from typing import Any

import httpx

from thesis_factory.domain.source import SourceRecord


_OPENALEX_FIELDS = ",".join(
    (
        "id",
        "doi",
        "title",
        "publication_year",
        "authorships",
        "primary_location",
        "abstract_inverted_index",
    )
)


class OpenAlexClient:
    BASE_URL = "https://api.openalex.org"

    def __init__(
            self,
            *,
            api_key: str | None = None,
            http_client: httpx.Client | None = None,
    ) -> None:
        self._api_key = api_key
        self._http_client = http_client or httpx.Client(
            base_url=self.BASE_URL,
            timeout=10.0,
        )
        self._owns_http_client = http_client is None

    def search_works(
            self,
            query: str,
            *,
            per_page: int = 10,
    ) -> tuple[SourceRecord, ...]:
        if not query.strip():
            raise ValueError("query must not be empty")

        if not 1 <= per_page <= 100:
            raise ValueError("per_page must be between 1 and 100")

        params: dict[str, str | int] = {
            "search": query,
            "per_page": per_page,
            "select": _OPENALEX_FIELDS,
        }

        if self._api_key:
            params["api_key"] = self._api_key

        response = self._http_client.get("/works", params=params)
        response.raise_for_status()

        payload = response.json()
        results = payload.get("results")

        if not isinstance(results, list):
            raise ValueError("OpenAlex response does not contain a results list")

        return tuple(_work_to_source_record(work) for work in results)

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()


def _work_to_source_record(work: Mapping[str, Any]) -> SourceRecord:
    authorships = work.get("authorships") or []

    authors = tuple(
        author_name
        for authorship in authorships
        if isinstance(authorship, Mapping)
        for author_name in [_extract_author_name(authorship)]
        if author_name is not None
    )

    return SourceRecord(
        title=work.get("title"),
        authors=authors,
        publication_year=work.get("publication_year"),
        doi=work.get("doi"),
        abstract=_reconstruct_abstract(
            work.get("abstract_inverted_index")
        ),
        venue=_extract_venue(work),
        provider="openalex",
        provider_id=work.get("id"),
    )


def _extract_author_name(authorship: Mapping[str, Any]) -> str | None:
    author = authorship.get("author")

    if not isinstance(author, Mapping):
        return None

    name = author.get("display_name")
    return name if isinstance(name, str) else None


def _extract_venue(work: Mapping[str, Any]) -> str | None:
    location = work.get("primary_location")

    if not isinstance(location, Mapping):
        return None

    source = location.get("source")

    if not isinstance(source, Mapping):
        return None

    venue = source.get("display_name")
    return venue if isinstance(venue, str) else None

def _reconstruct_abstract(value: Any) -> str | None:
    if not isinstance(value, Mapping) or not value:
        return None

    words: list[tuple[int, str]] = []

    for word, positions in value.items():
        if not isinstance(word, str):
            continue

        if not isinstance(positions, list):
            continue

        for position in positions:
            if isinstance(position, int) and position >= 0:
                words.append((position, word))

    if not words:
        return None

    words.sort(key=lambda item: item[0])

    return " ".join(word for _, word in words)