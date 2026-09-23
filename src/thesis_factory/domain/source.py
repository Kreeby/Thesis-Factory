from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

import html

class SourceRecord(BaseModel):
    """A normalized scholarly source discovered from an external provider."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    title: str = Field(min_length=1)
    authors: tuple[str, ...] = ()
    publication_year: int | None = None
    doi: str | None = None
    abstract: str | None = None
    venue: str | None = None

    provider: str = Field(min_length=1)
    provider_id: str = Field(min_length=1)

    @field_validator("doi", mode="before")
    @classmethod
    def normalize_doi(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        normalized = value.strip()

        for prefix in (
                "https://doi.org/",
                "http://doi.org/",
                "http://dx.doi.org/",
                "https://dx.doi.org/",
                "doi:",
        ):
            if normalized.lower().startswith(prefix):
                return normalized[len(prefix):].strip()

        return normalized

    @field_validator("title", "venue", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
    
        return html.unescape(value).strip()