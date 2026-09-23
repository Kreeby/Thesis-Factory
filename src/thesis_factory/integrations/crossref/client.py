from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

import httpx

from thesis_factory.domain.source import SourceRecord


class CrossrefClient:
    BASE_URL = "https://api.crossref.org"

    def __init__(
            self,
            *,
            mailto: str | None = None,
            http_client: httpx.Client | None = None,
    ) -> None:
        self._mailto = mailto

        self._http_client = http_client or httpx.Client(
            base_url=self.BASE_URL,
            timeout=10.0,
            headers={
                "User-Agent": (
                    "ThesisFactory/0.1.0 "
                    "(https://github.com/Kreeby/Thesis-Factory)"
                )
            },
        )

        self._owns_http_client = http_client is None

    def get_work_by_doi(self, doi: str) -> SourceRecord | None:
        normalized_doi = doi.strip()

        if not normalized_doi:
            raise ValueError("doi must not be empty")

        params = {}

        if self._mailto:
            params["mailto"] = self._mailto

        encoded_doi = quote(normalized_doi, safe="")

        response = self._http_client.get(
            f"/works/{encoded_doi}",
            params=params,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        payload = response.json()
        message = payload.get("message")

        if not isinstance(message, Mapping):
            raise ValueError(
                "Crossref response does not contain a work message"
            )

        return _work_to_source_record(message)

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()


def _work_to_source_record(work: Mapping[str, Any]) -> SourceRecord:
    title = _first_string(work.get("title"))

    if title is None:
        raise ValueError("Crossref work does not contain a title")

    authors = tuple(
        name
        for author in work.get("author") or []
        if isinstance(author, Mapping)
        for name in [_author_name(author)]
        if name is not None
    )

    return SourceRecord(
        title=title,
        authors=authors,
        publication_year=_publication_year(work),
        doi=work.get("DOI"),
        venue=_first_string(work.get("container-title")),
        provider="crossref",
        provider_id=str(work.get("DOI")),
    )


def _author_name(author: Mapping[str, Any]) -> str | None:
    given = author.get("given")
    family = author.get("family")

    parts = [
        value.strip()
        for value in (given, family)
        if isinstance(value, str) and value.strip()
    ]

    return " ".join(parts) or None


def _first_string(value: Any) -> str | None:
    if not isinstance(value, list) or not value:
        return None

    first = value[0]
    return first if isinstance(first, str) else None


def _publication_year(work: Mapping[str, Any]) -> int | None:
    for field in ("published-print", "published-online", "issued"):
        value = work.get(field)

        if not isinstance(value, Mapping):
            continue

        date_parts = value.get("date-parts")

        if (
                isinstance(date_parts, list)
                and date_parts
                and isinstance(date_parts[0], list)
                and date_parts[0]
                and isinstance(date_parts[0][0], int)
        ):
            return date_parts[0][0]

    return None