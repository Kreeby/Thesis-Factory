from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    VerifiedEvidenceResult,
)


class PrimarySourceParagraph(BaseModel):
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


class PrimarySourceDocument(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    normalization_version: str = (
        "primary-web-v1"
    )

    artifact_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$",
    )

    source_url: str = Field(
        min_length=1,
        max_length=4000,
    )

    source_host: str = Field(
        min_length=1,
        max_length=300,
    )

    title: str | None = Field(
        default=None,
        max_length=1000,
    )

    paragraphs: tuple[
        PrimarySourceParagraph,
        ...,
    ] = Field(
        min_length=1,
        max_length=10000,
    )

    @model_validator(
        mode="after",
    )
    def validate_unique_ordinals(
        self,
    ) -> Self:
        ordinals = [
            paragraph.ordinal
            for paragraph in self.paragraphs
        ]

        if (
            len(ordinals)
            != len(set(ordinals))
        ):
            raise ValueError(
                "primary-source paragraph "
                "ordinals must be unique"
            )

        return self


class PrimarySourceCandidate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    url: str = Field(
        min_length=1,
        max_length=4000,
    )

    title: str | None = Field(
        default=None,
        max_length=1000,
    )

    cited_text: str | None = Field(
        default=None,
        max_length=6000,
    )


class PrimarySourceAudit(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    url: str = Field(
        min_length=1,
        max_length=4000,
    )

    title: str | None = Field(
        default=None,
        max_length=1000,
    )

    host: str = Field(
        min_length=1,
        max_length=300,
    )

    authority_accepted: bool
    fetched: bool

    artifact_sha256: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{64}$",
    )

    note: str = Field(
        min_length=1,
        max_length=1600,
    )


class PrimaryTaskVerification(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    task_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )

    requirement: EvidenceRequirement

    evidence_result: VerifiedEvidenceResult

    sources: tuple[
        PrimarySourceAudit,
        ...,
    ] = Field(
        default=(),
        max_length=30,
    )

    errors: tuple[
        str,
        ...,
    ] = Field(
        default=(),
        max_length=30,
    )

    @model_validator(
        mode="after",
    )
    def validate_requirement_identity(
        self,
    ) -> Self:
        if (
            self.evidence_result.requirement_id
            != self.requirement.requirement_id
        ):
            raise ValueError(
                "evidence result requirement id "
                "must match task requirement"
            )

        return self


class PrimaryVerificationRun(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    topic: str = Field(
        min_length=1,
        max_length=500,
    )

    task_results: tuple[
        PrimaryTaskVerification,
        ...,
    ] = ()

    @model_validator(
        mode="after",
    )
    def validate_unique_tasks(
        self,
    ) -> Self:
        ids = [
            result.task_id
            for result in self.task_results
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "primary verification task ids "
                "must be unique"
            )

        return self
