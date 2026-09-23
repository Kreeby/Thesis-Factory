from pydantic import BaseModel, ConfigDict, Field


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