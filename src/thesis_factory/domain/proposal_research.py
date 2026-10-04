from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class ResearchDimension(StrEnum):
    PROBLEM = "PROBLEM"
    RESEARCH_GAP = "RESEARCH_GAP"
    RESEARCH_QUESTION = "RESEARCH_QUESTION"
    DATASET = "DATASET"
    BASELINE = "BASELINE"
    METHOD = "METHOD"
    METRIC = "METRIC"
    FEASIBILITY = "FEASIBILITY"
    CONTRIBUTION = "CONTRIBUTION"
    RISK = "RISK"
    DELIVERABLE = "DELIVERABLE"


class ResearchFindingState(StrEnum):
    SUPPORTED = "SUPPORTED"
    DERIVED = "DERIVED"
    ASSUMPTION = "ASSUMPTION"
    UNKNOWN = "UNKNOWN"


class ResearchFinding(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    finding_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )

    dimension: ResearchDimension

    statement: str = Field(
        min_length=1,
        max_length=1200,
    )

    rationale: str = Field(
        min_length=1,
        max_length=1500,
    )

    state: ResearchFindingState

    supporting_requirement_ids: tuple[
        str,
        ...,
    ] = Field(
        default=(),
        max_length=12,
    )

    @field_validator(
        "statement",
        "rationale",
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

    @model_validator(
        mode="after",
    )
    def validate_support_contract(
        self,
    ) -> Self:
        if (
            self.state
            in {
                ResearchFindingState.SUPPORTED,
                ResearchFindingState.DERIVED,
            }
            and not self.supporting_requirement_ids
        ):
            raise ValueError(
                "supported or derived finding "
                "requires evidence requirement ids"
            )

        if (
            self.state
            in {
                ResearchFindingState.ASSUMPTION,
                ResearchFindingState.UNKNOWN,
            }
            and self.supporting_requirement_ids
        ):
            raise ValueError(
                "assumption or unknown finding "
                "must not cite evidence requirements"
            )

        if (
            len(self.supporting_requirement_ids)
            != len(
                set(
                    self.supporting_requirement_ids
                )
            )
        ):
            raise ValueError(
                "supporting requirement ids "
                "must be unique"
            )

        return self


class ProposalResearchDraft(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    approved_topic: str = Field(
        min_length=1,
        max_length=500,
    )

    findings: tuple[
        ResearchFinding,
        ...,
    ] = Field(
        min_length=1,
        max_length=40,
    )

    @model_validator(
        mode="after",
    )
    def validate_unique_finding_ids(
        self,
    ) -> Self:
        ids = [
            finding.finding_id
            for finding in self.findings
        ]

        if len(ids) != len(set(ids)):
            raise ValueError(
                "finding ids must be unique"
            )

        return self


class CritiqueSeverity(StrEnum):
    BLOCKER = "BLOCKER"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class CritiqueIssue(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    issue_id: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9_-]*$",
    )

    severity: CritiqueSeverity

    finding_ids: tuple[
        str,
        ...,
    ] = Field(
        default=(),
        max_length=12,
    )

    problem: str = Field(
        min_length=1,
        max_length=1200,
    )

    required_action: str = Field(
        min_length=1,
        max_length=1200,
    )


class CritiqueVerdict(StrEnum):
    PASS = "PASS"
    REVISE = "REVISE"
    FAIL = "FAIL"


class ProposalCritique(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    verdict: CritiqueVerdict

    issues: tuple[
        CritiqueIssue,
        ...,
    ] = Field(
        default=(),
        max_length=30,
    )

    summary: str = Field(
        min_length=1,
        max_length=1500,
    )

    @model_validator(
        mode="after",
    )
    def validate_verdict(
        self,
    ) -> Self:
        blockers = [
            issue
            for issue in self.issues
            if (
                issue.severity
                == CritiqueSeverity.BLOCKER
            )
        ]

        if (
            self.verdict
            == CritiqueVerdict.PASS
            and self.issues
        ):
            raise ValueError(
                "PASS critique must not contain issues"
            )

        if (
            self.verdict
            == CritiqueVerdict.FAIL
            and not blockers
        ):
            raise ValueError(
                "FAIL critique requires blocker issue"
            )

        return self


class ProposalSectionKind(StrEnum):
    BACKGROUND_PROBLEM = "BACKGROUND_PROBLEM"
    RESEARCH_GAP = "RESEARCH_GAP"
    OBJECTIVES_RQS = "OBJECTIVES_RQS"
    RESEARCH_APPROACH = "RESEARCH_APPROACH"
    DATA_STRATEGY = "DATA_STRATEGY"
    EXPERIMENTAL_METHOD = "EXPERIMENTAL_METHOD"
    EVALUATION = "EVALUATION"
    EXPECTED_CONTRIBUTION = "EXPECTED_CONTRIBUTION"
    SOFTWARE_ARTIFACT = "SOFTWARE_ARTIFACT"
    SCOPE_RISKS = "SCOPE_RISKS"
    WORK_PLAN = "WORK_PLAN"
    DELIVERABLES = "DELIVERABLES"


class ProposalParagraphKind(StrEnum):
    EVIDENCE_BACKED = "EVIDENCE_BACKED"
    PROPOSED = "PROPOSED"
    LIMITATION = "LIMITATION"


class ProposalParagraph(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    kind: ProposalParagraphKind

    text: str = Field(
        min_length=1,
        max_length=3000,
    )

    finding_ids: tuple[
        str,
        ...,
    ] = Field(
        default=(),
        max_length=12,
    )

    @model_validator(
        mode="after",
    )
    def validate_finding_links(
        self,
    ) -> Self:
        if (
            self.kind
            == ProposalParagraphKind.EVIDENCE_BACKED
            and not self.finding_ids
        ):
            raise ValueError(
                "evidence-backed paragraph "
                "requires finding ids"
            )

        if (
            len(self.finding_ids)
            != len(set(self.finding_ids))
        ):
            raise ValueError(
                "paragraph finding ids must be unique"
            )

        return self


class ProposalSection(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    kind: ProposalSectionKind

    heading: str = Field(
        min_length=1,
        max_length=200,
    )

    paragraphs: tuple[
        ProposalParagraph,
        ...,
    ] = Field(
        min_length=1,
        max_length=12,
    )


class ProposalDocumentDraft(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    title: str = Field(
        min_length=1,
        max_length=300,
    )

    sections: tuple[
        ProposalSection,
        ...,
    ] = Field(
        min_length=1,
        max_length=12,
    )
