from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from thesis_factory.domain.thesis_requirements import (
    RequirementLevel,
    RequirementScope,
    ThesisRequirement,
    ThesisRequirementSet,
)


class RequirementAssessmentStatus(
    str,
    Enum,
):
    SATISFIED = "SATISFIED"
    UNSATISFIED = "UNSATISFIED"
    UNKNOWN = "UNKNOWN"


class UniversityFitStatus(
    str,
    Enum,
):
    PASS = "PASS"
    CONCERNS = "CONCERNS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class ResearchabilityDimension(
    str,
    Enum,
):
    UNIVERSITY_FIT = "UNIVERSITY_FIT"
    LITERATURE = "LITERATURE"
    DATASET = "DATASET"
    BASELINES = "BASELINES"
    METRICS = "METRICS"
    EXPERIMENT_FEASIBILITY = (
        "EXPERIMENT_FEASIBILITY"
    )
    CONTRIBUTION = "CONTRIBUTION"


class ResearchabilityDimensionStatus(
    str,
    Enum,
):
    PASS = "PASS"
    CONCERNS = "CONCERNS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class TopicResearchabilityStatus(
    str,
    Enum,
):
    RESEARCHABLE = "RESEARCHABLE"
    NOT_RESEARCHABLE = "NOT_RESEARCHABLE"
    HUMAN_REVIEW_REQUIRED = (
        "HUMAN_REVIEW_REQUIRED"
    )
    UNKNOWN = "UNKNOWN"


class UniversityRequirementAssessment(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    requirement_id: str = Field(
        pattern=(
            r"^[a-z0-9]+"
            r"(?:-[a-z0-9]+)*$"
        ),
    )

    status: RequirementAssessmentStatus

    rationale: str = Field(
        min_length=1,
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
        if not isinstance(
                value,
                str,
        ):
            return value

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "rationale must not be empty"
            )

        return normalized


class EvaluatedUniversityRequirement(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    requirement: ThesisRequirement

    status: RequirementAssessmentStatus

    rationale: str = Field(
        min_length=1,
    )


class UniversityFitEvaluation(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    requirement_set_id: str = Field(
        min_length=1,
    )

    topic: str = Field(
        min_length=1,
    )

    active_scopes: tuple[
        RequirementScope,
        ...,
    ] = Field(
        min_length=1,
    )

    status: UniversityFitStatus

    requirements: tuple[
        EvaluatedUniversityRequirement,
        ...,
    ] = Field(
        min_length=1,
    )

    blocking_requirement_ids: tuple[
        str,
        ...,
    ]

    unknown_required_requirement_ids: tuple[
        str,
        ...,
    ]

    concern_requirement_ids: tuple[
        str,
        ...,
    ]

    open_question_ids: tuple[
        str,
        ...,
    ]


class ResearchabilityDimensionAssessment(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    dimension: ResearchabilityDimension

    status: ResearchabilityDimensionStatus

    rationale: str = Field(
        min_length=1,
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
        if not isinstance(
                value,
                str,
        ):
            return value

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                "rationale must not be empty"
            )

        return normalized


class TopicResearchabilityReport(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    topic: str = Field(
        min_length=1,
    )

    university_fit: (
        UniversityFitEvaluation
    )

    dimensions: tuple[
        ResearchabilityDimensionAssessment,
        ...,
    ] = Field(
        min_length=1,
    )

    status: TopicResearchabilityStatus

    blocking_dimensions: tuple[
        ResearchabilityDimension,
        ...,
    ]

    unknown_dimensions: tuple[
        ResearchabilityDimension,
        ...,
    ]

    concern_dimensions: tuple[
        ResearchabilityDimension,
        ...,
    ]


def evaluate_university_fit(
        *,
        topic: str,
        requirement_set: ThesisRequirementSet,
        active_scopes: tuple[
            RequirementScope,
            ...,
        ],
        assessments: tuple[
            UniversityRequirementAssessment,
            ...,
        ] = (),
) -> UniversityFitEvaluation:
    normalized_topic = (
        topic.strip()
    )

    if not normalized_topic:
        raise ValueError(
            "topic must not be empty"
        )

    if not active_scopes:
        raise ValueError(
            "active_scopes must not be empty"
        )

    if (
            len(active_scopes)
            != len(set(active_scopes))
    ):
        raise ValueError(
            "active_scopes must be unique"
        )

    assessment_ids = [
        assessment.requirement_id
        for assessment
        in assessments
    ]

    if (
            len(assessment_ids)
            != len(set(assessment_ids))
    ):
        raise ValueError(
            "assessment requirement ids "
            "must be unique"
        )

    scope_set = set(
        active_scopes
    )

    applicable_requirements = tuple(
        requirement
        for requirement
        in requirement_set.requirements
        if (
                set(requirement.scopes)
                & scope_set
        )
    )

    if not applicable_requirements:
        raise ValueError(
            "no university requirements apply "
            "to the active scopes"
        )

    applicable_by_id = {
        requirement.id: requirement
        for requirement
        in applicable_requirements
    }

    assessment_by_id = {
        assessment.requirement_id: assessment
        for assessment
        in assessments
    }

    invalid_assessment_ids = (
            set(assessment_by_id)
            - set(applicable_by_id)
    )

    if invalid_assessment_ids:
        formatted = ", ".join(
            sorted(
                invalid_assessment_ids
            )
        )

        raise ValueError(
            "assessments reference requirements "
            "that are not applicable to the "
            f"active scopes: {formatted}"
        )

    evaluated: list[
        EvaluatedUniversityRequirement
    ] = []

    for requirement in (
            applicable_requirements
    ):
        assessment = (
            assessment_by_id.get(
                requirement.id
            )
        )

        if assessment is None:
            status = (
                RequirementAssessmentStatus
                .UNKNOWN
            )

            rationale = (
                "No assessment has been "
                "supplied for this requirement."
            )
        else:
            status = assessment.status
            rationale = (
                assessment.rationale
            )

        evaluated.append(
            EvaluatedUniversityRequirement(
                requirement=requirement,
                status=status,
                rationale=rationale,
            )
        )

    blocking_requirement_ids = tuple(
        item.requirement.id
        for item in evaluated
        if (
                item.requirement.level
                == RequirementLevel.REQUIRED
                and item.status
                == (
                    RequirementAssessmentStatus
                    .UNSATISFIED
                )
        )
    )

    unknown_required_requirement_ids = (
        tuple(
            item.requirement.id
            for item in evaluated
            if (
                    item.requirement.level
                    == RequirementLevel.REQUIRED
                    and item.status
                    == (
                        RequirementAssessmentStatus
                        .UNKNOWN
                    )
            )
        )
    )

    concern_requirement_ids = tuple(
        item.requirement.id
        for item in evaluated
        if (
                item.requirement.level
                == RequirementLevel.EXPECTED
                and item.status
                != (
                    RequirementAssessmentStatus
                    .SATISFIED
                )
        )
    )

    if blocking_requirement_ids:
        overall_status = (
            UniversityFitStatus.FAIL
        )

    elif unknown_required_requirement_ids:
        overall_status = (
            UniversityFitStatus.UNKNOWN
        )

    elif concern_requirement_ids:
        overall_status = (
            UniversityFitStatus.CONCERNS
        )

    else:
        overall_status = (
            UniversityFitStatus.PASS
        )

    return UniversityFitEvaluation(
        requirement_set_id=(
            requirement_set.id
        ),
        topic=normalized_topic,
        active_scopes=active_scopes,
        status=overall_status,
        requirements=tuple(
            evaluated
        ),
        blocking_requirement_ids=(
            blocking_requirement_ids
        ),
        unknown_required_requirement_ids=(
            unknown_required_requirement_ids
        ),
        concern_requirement_ids=(
            concern_requirement_ids
        ),
        open_question_ids=tuple(
            question.id
            for question
            in requirement_set.open_questions
        ),
    )


def build_topic_researchability_report(
        *,
        university_fit: UniversityFitEvaluation,
        assessments: tuple[
            ResearchabilityDimensionAssessment,
            ...,
        ] = (),
) -> TopicResearchabilityReport:
    supplied_dimensions = [
        assessment.dimension
        for assessment
        in assessments
    ]

    if (
            len(supplied_dimensions)
            != len(set(supplied_dimensions))
    ):
        raise ValueError(
            "researchability dimensions "
            "must be unique"
        )

    if (
            ResearchabilityDimension
                    .UNIVERSITY_FIT
            in supplied_dimensions
    ):
        raise ValueError(
            "UNIVERSITY_FIT is derived from "
            "university_fit and must not be "
            "supplied separately"
        )

    university_dimension_status = (
        _university_fit_dimension_status(
            university_fit.status
        )
    )

    dimensions_by_name = {
        assessment.dimension: assessment
        for assessment
        in assessments
    }

    dimensions_by_name[
        ResearchabilityDimension.UNIVERSITY_FIT
    ] = ResearchabilityDimensionAssessment(
        dimension=(
            ResearchabilityDimension
            .UNIVERSITY_FIT
        ),
        status=(
            university_dimension_status
        ),
        rationale=(
            "Derived from university-fit "
            f"evaluation: "
            f"{university_fit.status.value}."
        ),
    )

    ordered_dimensions = tuple(
        dimensions_by_name.get(
            dimension,
            ResearchabilityDimensionAssessment(
                dimension=dimension,
                status=(
                    ResearchabilityDimensionStatus
                    .UNKNOWN
                ),
                rationale=(
                    "This researchability "
                    "dimension has not yet "
                    "been assessed."
                ),
            ),
        )
        for dimension
        in ResearchabilityDimension
    )

    blocking_dimensions = tuple(
        item.dimension
        for item in ordered_dimensions
        if (
                item.status
                == (
                    ResearchabilityDimensionStatus
                    .FAIL
                )
        )
    )

    unknown_dimensions = tuple(
        item.dimension
        for item in ordered_dimensions
        if (
                item.status
                == (
                    ResearchabilityDimensionStatus
                    .UNKNOWN
                )
        )
    )

    concern_dimensions = tuple(
        item.dimension
        for item in ordered_dimensions
        if (
                item.status
                == (
                    ResearchabilityDimensionStatus
                    .CONCERNS
                )
        )
    )

    if blocking_dimensions:
        overall_status = (
            TopicResearchabilityStatus
            .NOT_RESEARCHABLE
        )

    elif unknown_dimensions:
        overall_status = (
            TopicResearchabilityStatus
            .UNKNOWN
        )

    elif concern_dimensions:
        overall_status = (
            TopicResearchabilityStatus
            .HUMAN_REVIEW_REQUIRED
        )

    else:
        overall_status = (
            TopicResearchabilityStatus
            .RESEARCHABLE
        )

    return TopicResearchabilityReport(
        topic=university_fit.topic,
        university_fit=university_fit,
        dimensions=ordered_dimensions,
        status=overall_status,
        blocking_dimensions=(
            blocking_dimensions
        ),
        unknown_dimensions=(
            unknown_dimensions
        ),
        concern_dimensions=(
            concern_dimensions
        ),
    )


def _university_fit_dimension_status(
        status: UniversityFitStatus,
) -> ResearchabilityDimensionStatus:
    mapping = {
        UniversityFitStatus.PASS: (
            ResearchabilityDimensionStatus
            .PASS
        ),
        UniversityFitStatus.CONCERNS: (
            ResearchabilityDimensionStatus
            .CONCERNS
        ),
        UniversityFitStatus.FAIL: (
            ResearchabilityDimensionStatus
            .FAIL
        ),
        UniversityFitStatus.UNKNOWN: (
            ResearchabilityDimensionStatus
            .UNKNOWN
        ),
    }

    return mapping[
        status
    ]