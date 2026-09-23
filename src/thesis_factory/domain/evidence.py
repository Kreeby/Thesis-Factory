from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class EvidenceAddress(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    artifact_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$",
    )

    normalization_version: str = Field(
        min_length=1,
    )

    paragraph_ordinal: int = Field(
        ge=1,
    )

    start_char: int = Field(
        ge=0,
    )

    end_char: int = Field(
        ge=1,
    )

    @model_validator(
        mode="after",
    )
    def validate_character_range(
            self,
    ) -> Self:
        if self.end_char <= self.start_char:
            raise ValueError(
                "end_char must be greater than start_char"
            )

        return self


class EvidenceSpan(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    address: EvidenceAddress

    text: str = Field(
        min_length=1,
    )

    source_provider: str = Field(
        min_length=1,
    )

    source_provider_id: str = Field(
        min_length=1,
    )

    section_ordinal: int = Field(
        ge=1,
    )

    section_path: tuple[
        str,
        ...,
    ] = Field(
        min_length=1,
    )