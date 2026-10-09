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
from thesis_factory.domain.source import (
    SourceRecord,
)


class ScholarlySourceAudit(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    source: SourceRecord

    registry_source: SourceRecord | None = None

    fulltext_url: str | None = Field(
        default=None,
        max_length=4000,
    )

    artifact_sha256: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{64}$",
    )

    usable_fulltext: bool

    note: str = Field(
        min_length=1,
        max_length=1200,
    )


class ScholarlyTaskVerification(BaseModel):
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
        ScholarlySourceAudit,
        ...,
    ] = Field(
        default=(),
        max_length=12,
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


class ScholarlyVerificationRun(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    topic: str = Field(
        min_length=1,
        max_length=500,
    )

    task_results: tuple[
        ScholarlyTaskVerification,
        ...,
    ] = ()

    @model_validator(
        mode="after",
    )
    def validate_unique_task_results(
        self,
    ) -> Self:
        ids = [
            result.task_id
            for result in self.task_results
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "scholarly task result ids must be unique"
            )

        return self
