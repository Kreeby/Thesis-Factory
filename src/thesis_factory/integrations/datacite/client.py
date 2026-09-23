from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

import httpx

from thesis_factory.domain.source import SourceRecord


class DataCiteClient:
    BASE_URL = "https://api.datacite.org"

    def __init__(
            self,
            *,
            http_client: httpx.Client | None = None,
    ) -> None:
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

    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        normalized_doi = doi.strip()

        if not normalized_doi:
            raise ValueError("doi must not be empty")

        encoded_doi = quote(
            normalized_doi,
            safe="",
        )

        response = self._http_client.get(
            f"/dois/{encoded_doi}"
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        payload = response.json()
        data = payload.get("data")

        if not isinstance(data, Mapping):
            raise ValueError(
                "DataCite response does not contain data"
            )

        attributes = data.get("attributes")

        if not isinstance(attributes, Mapping):
            raise ValueError(
                "DataCite response does not contain attributes"
            )

        return _doi_to_source_record(
            data,
            attributes,
        )

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()


def _doi_to_source_record(
        data: Mapping[str, Any],
        attributes: Mapping[str, Any],
) -> SourceRecord:
    title = _title(attributes.get("titles"))

    if title is None:
        raise ValueError(
            "DataCite DOI does not contain a title"
        )

    return SourceRecord(
        title=title,
        authors=_authors(
            attributes.get("creators")
        ),
        publication_year=_publication_year(
            attributes.get("publicationYear")
        ),
        doi=attributes.get("doi") or data.get("id"),
        abstract=_abstract(
            attributes.get("descriptions")
        ),
        provider="datacite",
        provider_id=str(
            attributes.get("doi") or data.get("id")
        ),
    )


def _title(value: Any) -> str | None:
    if not isinstance(value, list):
        return None

    for item in value:
        if not isinstance(item, Mapping):
            continue

        title = item.get("title")

        if isinstance(title, str) and title.strip():
            return title

    return None


def _authors(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()

    authors: list[str] = []

    for creator in value:
        if not isinstance(creator, Mapping):
            continue

        name = creator.get("name")

        if isinstance(name, str) and name.strip():
            authors.append(name.strip())
            continue

        given = creator.get("givenName")
        family = creator.get("familyName")

        parts = [
            part.strip()
            for part in (given, family)
            if isinstance(part, str) and part.strip()
        ]

        if parts:
            authors.append(" ".join(parts))

    return tuple(authors)


def _publication_year(value: Any) -> int | None:
    if isinstance(value, int):
        return value

    if isinstance(value, str) and value.isdigit():
        return int(value)

    return None


def _abstract(value: Any) -> str | None:
    if not isinstance(value, list):
        return None

    for description in value:
        if not isinstance(description, Mapping):
            continue

        if description.get("descriptionType") != "Abstract":
            continue

        text = description.get("description")

        if isinstance(text, str) and text.strip():
            return " ".join(
                text.split()
            )

    return None