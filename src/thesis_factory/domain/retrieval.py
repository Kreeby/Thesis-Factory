from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from thesis_factory.domain.document import (
    DocumentSectionKind,
    SectionHeadingRole,
)


class RetrievalUnitId(BaseModel):
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


class RetrievalUnit(BaseModel):
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

    section_kind: DocumentSectionKind

    heading_role: SectionHeadingRole

    paragraph_ordinal: int = Field(
        ge=1,
    )

    text: str = Field(
        min_length=1,
    )

    @property
    def identity(
            self,
    ) -> RetrievalUnitId:
        return RetrievalUnitId(
            artifact_sha256=(
                self.artifact_sha256
            ),
            normalization_version=(
                self.normalization_version
            ),
            paragraph_ordinal=(
                self.paragraph_ordinal
            ),
        )


class RetrievalHit(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    unit: RetrievalUnit

    score: float = Field(
        gt=0,
    )