from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class SourceTextLocationKind(StrEnum):
    OPENALEX_GROBID_XML = "OPENALEX_GROBID_XML"
    OPENALEX_PDF = "OPENALEX_PDF"
    ORIGINAL_PDF = "ORIGINAL_PDF"
    LANDING_PAGE = "LANDING_PAGE"


class SourceTextLocation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    kind: SourceTextLocationKind

    url: str

    provider: str

    provider_work_id: str

    host_name: str | None = None

    version: str | None = None

    license: str | None = None

    is_open_access: bool