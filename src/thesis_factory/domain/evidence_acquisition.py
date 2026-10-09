from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from thesis_factory.domain.evidence import (
    EvidenceSpan,
)
from thesis_factory.domain.retrieval import (
    RetrievalUnit,
    RetrievalUnitId,
)


class EvidenceRequirementKind(StrEnum):
    LITERATURE = "LITERATURE"
    LEGAL = "LEGAL"
    DATASET = "DATASET"
    BASELINE = "BASELINE"
    METHOD = "METHOD"
    METRIC = "METRIC"
    FEASIBILITY = "FEASIBILITY"
    CONTRIBUTION = "CONTRIBUTION"


class EvidenceRequirement(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    requirement_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )

    kind: EvidenceRequirementKind

    question: str = Field(
        min_length=1,
        max_length=500,
    )

    why_needed: str = Field(
        min_length=1,
        max_length=500,
    )

    @field_validator(
        "question",
        "why_needed",
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
                "value must not be empty"
            )

        return normalized


class EvidenceQuery(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    query: str = Field(
        min_length=1,
        max_length=300,
    )

    @field_validator(
        "query",
        mode="before",
    )
    @classmethod
    def normalize_query(
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
                "query must not be empty"
            )

        return normalized


class EvidenceQueryPlan(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    requirement_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )

    queries: tuple[
        EvidenceQuery,
        ...,
    ] = Field(
        min_length=1,
        max_length=4,
    )

    @model_validator(
        mode="after",
    )
    def validate_unique_queries(
            self,
    ) -> Self:
        normalized = [
            query.query.casefold()
            for query in self.queries
        ]

        if (
                len(normalized)
                != len(set(normalized))
        ):
            raise ValueError(
                "evidence queries must be unique"
            )

        return self


class EvidenceContext(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    hit_identity: RetrievalUnitId

    units: tuple[
        RetrievalUnit,
        ...,
    ] = Field(
        min_length=1,
    )

    @model_validator(
        mode="after",
    )
    def validate_context(
            self,
    ) -> Self:
        identities = [
            unit.identity
            for unit in self.units
        ]

        if (
                len(identities)
                != len(set(identities))
        ):
            raise ValueError(
                "context contains duplicate units"
            )

        if (
                self.hit_identity
                not in identities
        ):
            raise ValueError(
                "context must contain retrieval hit"
            )

        artifact_ids = {
            unit.artifact_sha256
            for unit in self.units
        }

        normalization_versions = {
            unit.normalization_version
            for unit in self.units
        }

        if len(artifact_ids) != 1:
            raise ValueError(
                "context must belong to one artifact"
            )

        if (
                len(normalization_versions)
                != 1
        ):
            raise ValueError(
                "context must use one normalization version"
            )

        return self


class EvidenceSupportStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    INSUFFICIENT_EVIDENCE = (
        "INSUFFICIENT_EVIDENCE"
    )


class EvidenceQuoteProposal(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    paragraph_ordinal: int = Field(
        ge=1,
    )

    exact_quote: str = Field(
        min_length=1,
        max_length=3000,
    )

    @field_validator(
        "exact_quote",
        mode="before",
    )
    @classmethod
    def normalize_quote(
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
                "exact quote must not be empty"
            )

        return normalized


class EvidenceExtractionProposal(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    requirement_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )

    status: EvidenceSupportStatus

    rationale: str = Field(
        min_length=1,
        max_length=1000,
    )

    quotes: tuple[
        EvidenceQuoteProposal,
        ...,
    ] = Field(
        default=(),
        max_length=4,
    )

    @field_validator(
        "rationale",
        mode="before",
    )
    @classmethod
    def normalize_rationale(
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
                "rationale must not be empty"
            )

        return normalized

    @model_validator(
        mode="after",
    )
    def validate_status_and_quotes(
            self,
    ) -> Self:
        if (
                self.status
                in {
                    EvidenceSupportStatus.SUPPORTED,
                    EvidenceSupportStatus.PARTIAL,
                }
                and not self.quotes
        ):
            raise ValueError(
                "supported or partial evidence "
                "requires at least one quote"
            )

        if (
                self.status
                in {
                    EvidenceSupportStatus.NOT_SUPPORTED,
                    EvidenceSupportStatus.INSUFFICIENT_EVIDENCE,
                }
                and self.quotes
        ):
            raise ValueError(
                "unsupported or insufficient evidence "
                "must not contain quotes"
            )

        return self


class VerifiedEvidenceResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    requirement_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )

    status: EvidenceSupportStatus

    rationale: str = Field(
        min_length=1,
    )

    evidence: tuple[
        EvidenceSpan,
        ...,
    ] = ()
