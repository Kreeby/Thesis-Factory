import time
from collections.abc import Mapping
from enum import StrEnum
from typing import Any

import httpx

from thesis_factory.domain.source import SourceRecord
from thesis_factory.domain.source_text import (
    SourceTextLocation,
    SourceTextLocationKind,
)


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


class OpenAlexSearchMode(StrEnum):
    LEXICAL = "LEXICAL"
    SEMANTIC = "SEMANTIC"


class OpenAlexClient:
    BASE_URL = "https://api.openalex.org"

    def __init__(
            self,
            *,
            api_key: str | None = None,
            search_mode: OpenAlexSearchMode = OpenAlexSearchMode.LEXICAL,
            semantic_min_interval_seconds: float = 1.05,
            http_client: httpx.Client | None = None,
    ) -> None:
        if semantic_min_interval_seconds < 0:
            raise ValueError(
                "semantic_min_interval_seconds must not be negative"
            )

        self._api_key = api_key
        self._search_mode = search_mode
        self._semantic_min_interval_seconds = (
            semantic_min_interval_seconds
        )
        self._last_semantic_request_at: float | None = None

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
        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("query must not be empty")

        max_per_page = (
            50
            if self._search_mode == OpenAlexSearchMode.SEMANTIC
            else 100
        )

        if not 1 <= per_page <= max_per_page:
            raise ValueError(
                f"per_page must be between 1 and {max_per_page}"
            )

        search_parameter = (
            "search.semantic"
            if self._search_mode == OpenAlexSearchMode.SEMANTIC
            else "search"
        )

        params: dict[str, str | int] = {
            search_parameter: normalized_query,
            "per_page": per_page,
            "select": _OPENALEX_FIELDS,
        }

        if self._api_key:
            params["api_key"] = self._api_key

        self._wait_for_semantic_rate_limit()

        response = self._http_client.get(
            "/works",
            params=params,
        )
        response.raise_for_status()

        payload = response.json()
        results = payload.get("results")

        if not isinstance(results, list):
            raise ValueError(
                "OpenAlex response does not contain a results list"
            )

        return tuple(
            _work_to_source_record(work)
            for work in results
        )

    def get_text_locations(
            self,
            source: SourceRecord,
    ) -> tuple[SourceTextLocation, ...]:
        if source.provider != "openalex":
            raise ValueError(
                "source must originate from OpenAlex"
            )

        work_id = _openalex_work_id(
            source.provider_id
        )

        params: dict[str, str] = {
            "select": (
                "id,"
                "best_oa_location,"
                "locations,"
                "content_urls"
            )
        }

        if self._api_key:
            params["api_key"] = self._api_key

        response = self._http_client.get(
            f"/works/{work_id}",
            params=params,
        )
        response.raise_for_status()

        payload = response.json()

        return _extract_text_locations(
            payload
        )

    def _wait_for_semantic_rate_limit(self) -> None:
        if self._search_mode != OpenAlexSearchMode.SEMANTIC:
            return

        now = time.monotonic()

        if self._last_semantic_request_at is not None:
            elapsed = (
                    now
                    - self._last_semantic_request_at
            )

            remaining = (
                    self._semantic_min_interval_seconds
                    - elapsed
            )

            if remaining > 0:
                time.sleep(remaining)

        self._last_semantic_request_at = time.monotonic()

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()


def _work_to_source_record(
        work: Mapping[str, Any],
) -> SourceRecord:
    authorships = work.get("authorships") or []

    authors = tuple(
        author_name
        for authorship in authorships
        if isinstance(authorship, Mapping)
        for author_name in [
            _extract_author_name(authorship)
        ]
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


def _extract_author_name(
        authorship: Mapping[str, Any],
) -> str | None:
    author = authorship.get("author")

    if not isinstance(author, Mapping):
        return None

    name = author.get("display_name")

    return (
        name
        if isinstance(name, str)
        else None
    )


def _extract_venue(
        work: Mapping[str, Any],
) -> str | None:
    location = work.get("primary_location")

    if not isinstance(location, Mapping):
        return None

    source = location.get("source")

    if not isinstance(source, Mapping):
        return None

    venue = source.get("display_name")

    return (
        venue
        if isinstance(venue, str)
        else None
    )


def _reconstruct_abstract(
        value: Any,
) -> str | None:
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
                words.append(
                    (position, word)
                )

    if not words:
        return None

    words.sort(
        key=lambda item: item[0]
    )

    return " ".join(
        word
        for _, word in words
    )


def _openalex_work_id(
        provider_id: str,
) -> str:
    normalized = provider_id.strip()

    if not normalized:
        raise ValueError(
            "OpenAlex provider_id must not be empty"
        )

    prefix = "https://openalex.org/"

    if normalized.startswith(prefix):
        normalized = normalized[len(prefix):]

    if not normalized.startswith("W"):
        raise ValueError(
            "invalid OpenAlex work id"
        )

    return normalized


def _extract_text_locations(
        work: Mapping[str, Any],
) -> tuple[SourceTextLocation, ...]:
    work_id = work.get("id")

    if not isinstance(work_id, str) or not work_id.strip():
        raise ValueError(
            "OpenAlex work does not contain an id"
        )

    locations: list[SourceTextLocation] = []

    # ------------------------------------------------------------
    # OpenAlex-hosted full text
    # ------------------------------------------------------------

    content_urls = work.get("content_urls")

    if isinstance(content_urls, Mapping):
        grobid_xml = content_urls.get(
            "grobid_xml"
        )

        if (
                isinstance(grobid_xml, str)
                and grobid_xml.strip()
        ):
            locations.append(
                SourceTextLocation(
                    kind=(
                        SourceTextLocationKind
                        .OPENALEX_GROBID_XML
                    ),
                    url=grobid_xml.strip(),
                    provider="openalex",
                    provider_work_id=work_id,
                    is_open_access=True,
                )
            )

        pdf = content_urls.get("pdf")

        if isinstance(pdf, str) and pdf.strip():
            locations.append(
                SourceTextLocation(
                    kind=(
                        SourceTextLocationKind
                        .OPENALEX_PDF
                    ),
                    url=pdf.strip(),
                    provider="openalex",
                    provider_work_id=work_id,
                    is_open_access=True,
                )
            )

    # ------------------------------------------------------------
    # OpenAlex preferred OA location
    # ------------------------------------------------------------

    best_oa = work.get(
        "best_oa_location"
    )

    if isinstance(best_oa, Mapping):
        _append_openalex_location(
            locations,
            work_id=work_id,
            location=best_oa,
        )

    # ------------------------------------------------------------
    # Every other OA location known to OpenAlex
    # ------------------------------------------------------------

    raw_locations = work.get(
        "locations"
    )

    if isinstance(raw_locations, list):
        for location in raw_locations:
            if not isinstance(location, Mapping):
                continue

            if location.get("is_oa") is not True:
                continue

            _append_openalex_location(
                locations,
                work_id=work_id,
                location=location,
            )

    return tuple(
        _deduplicate_locations(
            locations
        )
    )


def _append_openalex_location(
        locations: list[SourceTextLocation],
        *,
        work_id: str,
        location: Mapping[str, Any],
) -> None:
    source = location.get("source")

    host_name = None

    if isinstance(source, Mapping):
        display_name = source.get(
            "display_name"
        )

        if (
                isinstance(display_name, str)
                and display_name.strip()
        ):
            host_name = display_name.strip()

    version = location.get("version")
    license_value = location.get("license")

    normalized_version = (
        version
        if isinstance(version, str)
        else None
    )

    normalized_license = (
        license_value
        if isinstance(license_value, str)
        else None
    )

    pdf_url = location.get(
        "pdf_url"
    )

    if (
            isinstance(pdf_url, str)
            and pdf_url.strip()
    ):
        locations.append(
            SourceTextLocation(
                kind=(
                    SourceTextLocationKind
                    .ORIGINAL_PDF
                ),
                url=pdf_url.strip(),
                provider="openalex",
                provider_work_id=work_id,
                host_name=host_name,
                version=normalized_version,
                license=normalized_license,
                is_open_access=True,
            )
        )

    landing_page_url = location.get(
        "landing_page_url"
    )

    if (
            isinstance(
                landing_page_url,
                str,
            )
            and landing_page_url.strip()
    ):
        locations.append(
            SourceTextLocation(
                kind=(
                    SourceTextLocationKind
                    .LANDING_PAGE
                ),
                url=landing_page_url.strip(),
                provider="openalex",
                provider_work_id=work_id,
                host_name=host_name,
                version=normalized_version,
                license=normalized_license,
                is_open_access=True,
            )
        )


def _deduplicate_locations(
        locations: list[SourceTextLocation],
) -> list[SourceTextLocation]:
    seen_urls: set[str] = set()
    result: list[SourceTextLocation] = []

    for location in locations:
        if location.url in seen_urls:
            continue

        seen_urls.add(
            location.url
        )

        result.append(
            location
        )

    return result