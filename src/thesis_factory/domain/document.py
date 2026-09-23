from enum import StrEnum
from typing import Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class DocumentSectionKind(StrEnum):
    ABSTRACT = "ABSTRACT"
    BODY = "BODY"


class SectionHeadingRole(StrEnum):
    STANDARD = "STANDARD"
    TABLE = "TABLE"
    FIGURE = "FIGURE"


class NormalizedParagraph(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    ordinal: int = Field(
        ge=1,
    )

    text: str = Field(
        min_length=1,
    )

    source_xml_id: str | None = None

    @field_validator(
        "text",
        mode="before",
    )
    @classmethod
    def normalize_text(
            cls,
            value: str,
    ) -> str:
        if not isinstance(value, str):
            return value

        normalized = " ".join(
            value.split()
        )

        if not normalized:
            raise ValueError(
                "paragraph text must not be empty"
            )

        return normalized


class NormalizedSection(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    ordinal: int = Field(
        ge=1,
    )

    kind: DocumentSectionKind

    heading_role: SectionHeadingRole = (
        SectionHeadingRole.STANDARD
    )

    path: tuple[str, ...] = Field(
        min_length=1,
    )

    paragraphs: tuple[
        NormalizedParagraph,
        ...,
    ] = Field(
        min_length=1,
    )

    @field_validator(
        "path",
        mode="before",
    )
    @classmethod
    def normalize_path(
            cls,
            value: tuple[str, ...],
    ) -> tuple[str, ...]:
        normalized = tuple(
            item.strip()
            for item in value
            if isinstance(item, str)
            and item.strip()
        )

        if not normalized:
            raise ValueError(
                "section path must not be empty"
            )

        return normalized


class NormalizedDocument(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    normalization_version: Literal[
        "grobid-tei-v1"
    ] = "grobid-tei-v1"

    artifact_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$",
    )

    source_provider: str = Field(
        min_length=1,
    )

    source_provider_id: str = Field(
        min_length=1,
    )

    title: str | None = None

    sections: tuple[
        NormalizedSection,
        ...,
    ] = Field(
        min_length=1,
    )

    @model_validator(
        mode="after",
    )
    def validate_unique_ordinals(
            self,
    ) -> Self:
        section_ordinals = [
            section.ordinal
            for section in self.sections
        ]

        if (
                len(section_ordinals)
                != len(set(section_ordinals))
        ):
            raise ValueError(
                "section ordinals must be unique"
            )

        paragraph_ordinals = [
            paragraph.ordinal
            for section in self.sections
            for paragraph in section.paragraphs
        ]

        if (
                len(paragraph_ordinals)
                != len(set(paragraph_ordinals))
        ):
            raise ValueError(
                "paragraph ordinals must be unique"
            )

        return self