import hashlib
from enum import StrEnum
from urllib.parse import urlsplit

import httpx
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from thesis_factory.domain.source_text import (
    SourceTextLocation,
    SourceTextLocationKind,
)


class ArtifactFormat(StrEnum):
    GROBID_XML = "GROBID_XML"
    PDF = "PDF"


class ArtifactFetchError(
    ValueError
):
    pass


class FetchedArtifact(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    location: SourceTextLocation
    format: ArtifactFormat

    content: bytes = Field(
        min_length=1,
        repr=False,
    )

    sha256: str = Field(
        min_length=64,
        max_length=64,
    )

    content_length: int = Field(
        gt=0,
    )

    response_content_type: str | None = None


class ArtifactFetcher:
    def __init__(
            self,
            *,
            max_bytes: int = 25 * 1024 * 1024,
            openalex_api_key: str | None = None,
            http_client: httpx.Client | None = None,
    ) -> None:
        if max_bytes < 1:
            raise ValueError(
                "max_bytes must be positive"
            )

        self._max_bytes = max_bytes

        normalized_key = (
            openalex_api_key.strip()
            if isinstance(
                openalex_api_key,
                str,
            )
            else None
        )

        self._openalex_api_key = (
            normalized_key
            or None
        )

        self._http_client = (
                http_client
                or httpx.Client(
            timeout=30.0,
            follow_redirects=True,
        )
        )

        self._owns_http_client = (
            http_client is None
        )

    def fetch(
            self,
            location: SourceTextLocation,
    ) -> FetchedArtifact:
        artifact_format = _artifact_format(
            location
        )

        openalex_content = (
            _is_openalex_content_url(
                location.url
            )
        )

        params = None

        if openalex_content:
            if self._openalex_api_key is None:
                raise ArtifactFetchError(
                    "OpenAlex content download "
                    "requires an API key"
                )

            params = {
                "api_key": (
                    self._openalex_api_key
                )
            }

        response = self._http_client.get(
            location.url,
            params=params,
        )

        if (
                openalex_content
                and response.is_error
        ):
            # Do not call raise_for_status() here:
            # the request URL contains the API key
            # as a query parameter and must never
            # appear in logs or persisted errors.
            raise ArtifactFetchError(
                "OpenAlex content download failed "
                f"with HTTP {response.status_code} "
                f"for {_safe_url(location.url)}"
            )

        response.raise_for_status()

        content = response.content

        if not content:
            raise ValueError(
                "downloaded artifact is empty"
            )

        if len(content) > self._max_bytes:
            raise ValueError(
                "downloaded artifact exceeds maximum size"
            )

        _validate_content(
            content,
            artifact_format=artifact_format,
        )

        digest = hashlib.sha256(
            content
        ).hexdigest()

        return FetchedArtifact(
            location=location,
            format=artifact_format,
            content=content,
            sha256=digest,
            content_length=len(content),
            response_content_type=(
                response.headers.get(
                    "content-type"
                )
            ),
        )

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()


def select_preferred_text_location(
        locations: tuple[
            SourceTextLocation,
            ...,
        ],
) -> SourceTextLocation | None:
    priorities = (
        SourceTextLocationKind.OPENALEX_GROBID_XML,
        SourceTextLocationKind.OPENALEX_PDF,
        SourceTextLocationKind.ORIGINAL_PDF,
    )

    for kind in priorities:
        for location in locations:
            if location.kind == kind:
                return location

    return None


def _artifact_format(
        location: SourceTextLocation,
) -> ArtifactFormat:
    if (
            location.kind
            == SourceTextLocationKind.OPENALEX_GROBID_XML
    ):
        return ArtifactFormat.GROBID_XML

    if location.kind in {
        SourceTextLocationKind.OPENALEX_PDF,
        SourceTextLocationKind.ORIGINAL_PDF,
    }:
        return ArtifactFormat.PDF

    raise ValueError(
        "location does not point directly to supported full text"
    )


def _is_openalex_content_url(
        url: str,
) -> bool:
    return (
        urlsplit(url).hostname
        == "content.openalex.org"
    )


def _safe_url(
        url: str,
) -> str:
    parsed = urlsplit(
        url
    )

    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
        f"{parsed.path}"
    )


def _validate_content(
        content: bytes,
        *,
        artifact_format: ArtifactFormat,
) -> None:
    if artifact_format == ArtifactFormat.PDF:
        if not content.startswith(b"%PDF-"):
            raise ValueError(
                "downloaded content is not a PDF"
            )

        return

    if artifact_format == ArtifactFormat.GROBID_XML:
        prefix = content.lstrip()[:100].lower()

        if (
                b"<?xml" not in prefix
                and b"<tei" not in prefix
                and b"<html" not in prefix
        ):
            raise ValueError(
                "downloaded content does not look like GROBID XML"
            )
