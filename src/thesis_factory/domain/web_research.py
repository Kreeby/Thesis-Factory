from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from thesis_factory.domain.proposal_research import (
    ResearchDimension,
)


class WebCitation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    citation_id: str = Field(
        min_length=2,
        max_length=20,
        pattern=r"^c[1-9][0-9]*$",
    )

    url: HttpUrl
    title: str | None = None
    cited_text: str = Field(
        min_length=1,
        max_length=6000,
    )

    @field_validator(
        "title",
        "cited_text",
        mode="before",
    )
    @classmethod
    def normalize_text(
        cls,
        value,
    ):
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        normalized = " ".join(
            value.split()
        )

        if not normalized:
            return value

        return normalized


class WebResearchPacket(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    objective: str = Field(
        min_length=1,
        max_length=1000,
    )

    narrative: str = Field(
        min_length=1,
    )

    citations: tuple[
        WebCitation,
        ...,
    ] = Field(
        min_length=1,
        max_length=100,
    )

    @field_validator(
        "objective",
        "narrative",
        mode="before",
    )
    @classmethod
    def normalize_packet_text(
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

    @model_validator(
        mode="after",
    )
    def validate_unique_citation_ids(
        self,
    ) -> Self:
        ids = [
            citation.citation_id
            for citation in self.citations
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "citation ids must be unique"
            )

        return self


class ResearchLeadState(StrEnum):
    DISCOVERED = "DISCOVERED"


class ResearchLead(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    lead_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )

    dimension: ResearchDimension

    candidate_statement: str = Field(
        min_length=1,
        max_length=700,
    )

    why_relevant: str = Field(
        min_length=1,
        max_length=700,
    )

    source_citation_ids: tuple[
        str,
        ...,
    ] = Field(
        min_length=1,
        max_length=6,
    )

    verification_need: str = Field(
        min_length=1,
        max_length=700,
    )

    state: ResearchLeadState = (
        ResearchLeadState.DISCOVERED
    )

    @field_validator(
        "candidate_statement",
        "why_relevant",
        "verification_need",
        mode="before",
    )
    @classmethod
    def normalize_lead_text(
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

    @model_validator(
        mode="after",
    )
    def validate_unique_citation_ids(
        self,
    ) -> Self:
        if (
            len(self.source_citation_ids)
            != len(set(self.source_citation_ids))
        ):
            raise ValueError(
                "lead citation ids must be unique"
            )

        return self


class ResearchLeadSet(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    objective: str = Field(
        min_length=1,
        max_length=1000,
    )

    leads: tuple[
        ResearchLead,
        ...,
    ] = Field(
        min_length=1,
        max_length=10,
    )

    @model_validator(
        mode="after",
    )
    def validate_unique_ids(
        self,
    ) -> Self:
        ids = [
            lead.lead_id
            for lead in self.leads
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "research lead ids must be unique"
            )

        return self
