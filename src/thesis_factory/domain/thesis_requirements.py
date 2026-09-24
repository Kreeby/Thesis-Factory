from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class RequirementLevel(
    str,
    Enum,
):
    REQUIRED = "REQUIRED"
    EXPECTED = "EXPECTED"
    GUIDANCE = "GUIDANCE"


class RequirementAuthority(
    str,
    Enum,
):
    FACULTY_REQUIREMENT = (
        "FACULTY_REQUIREMENT"
    )

    DEPARTMENT_GUIDANCE = (
        "DEPARTMENT_GUIDANCE"
    )

    EIT_GUIDANCE = (
        "EIT_GUIDANCE"
    )

    GUIDE_SUMMARY = (
        "GUIDE_SUMMARY"
    )


class RequirementScope(
    str,
    Enum,
):
    MSC = "MSC"
    EIT = "EIT"


class RequirementCategory(
    str,
    Enum,
):
    TOPIC_FIT = "TOPIC_FIT"
    RESEARCH = "RESEARCH"
    METHOD = "METHOD"
    ENGINEERING = "ENGINEERING"
    NOVELTY = "NOVELTY"
    VALIDATION = "VALIDATION"
    CONTRIBUTION = "CONTRIBUTION"
    INDEPENDENCE = "INDEPENDENCE"
    FEASIBILITY = "FEASIBILITY"


class ThesisRequirement(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    id: str = Field(
        pattern=(
            r"^[a-z0-9]+"
            r"(?:-[a-z0-9]+)*$"
        ),
    )

    category: RequirementCategory

    level: RequirementLevel

    authority: RequirementAuthority

    scopes: tuple[
        RequirementScope,
        ...,
    ] = Field(
        min_length=1,
    )

    statement: str = Field(
        min_length=1,
    )

    source_pages: tuple[
        int,
        ...,
    ] = Field(
        min_length=1,
    )

    @field_validator(
        "source_pages",
    )
    @classmethod
    def validate_source_pages(
            cls,
            pages: tuple[
                int,
                ...,
            ],
    ) -> tuple[
        int,
        ...,
    ]:
        if any(
                page < 1
                for page in pages
        ):
            raise ValueError(
                "source pages must be positive"
            )

        if (
                len(pages)
                != len(set(pages))
        ):
            raise ValueError(
                "source pages must be unique"
            )

        if pages != tuple(
                sorted(pages)
        ):
            raise ValueError(
                "source pages must be sorted"
            )

        return pages


class RequirementOpenQuestion(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    id: str = Field(
        pattern=(
            r"^[a-z0-9]+"
            r"(?:-[a-z0-9]+)*$"
        ),
    )

    question: str = Field(
        min_length=1,
    )

    reason: str = Field(
        min_length=1,
    )

    source_pages: tuple[
        int,
        ...,
    ] = Field(
        min_length=1,
    )

    @field_validator(
        "source_pages",
    )
    @classmethod
    def validate_source_pages(
            cls,
            pages: tuple[
                int,
                ...,
            ],
    ) -> tuple[
        int,
        ...,
    ]:
        if any(
                page < 1
                for page in pages
        ):
            raise ValueError(
                "source pages must be positive"
            )

        if (
                len(pages)
                != len(set(pages))
        ):
            raise ValueError(
                "source pages must be unique"
            )

        if pages != tuple(
                sorted(pages)
        ):
            raise ValueError(
                "source pages must be sorted"
            )

        return pages


class ThesisRequirementSet(
    BaseModel
):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    id: str = Field(
        pattern=(
            r"^[a-z0-9]+"
            r"(?:-[a-z0-9]+)*$"
        ),
    )

    institution: str = Field(
        min_length=1,
    )

    faculty: str = Field(
        min_length=1,
    )

    source_title: str = Field(
        min_length=1,
    )

    source_sha256: str = Field(
        pattern=r"^[0-9a-f]{64}$",
    )

    requirements: tuple[
        ThesisRequirement,
        ...,
    ] = Field(
        min_length=1,
    )

    open_questions: tuple[
        RequirementOpenQuestion,
        ...,
    ] = ()

    @model_validator(
        mode="after",
    )
    def validate_unique_ids(
            self,
    ) -> "ThesisRequirementSet":
        requirement_ids = [
            requirement.id
            for requirement
            in self.requirements
        ]

        if (
                len(requirement_ids)
                != len(
            set(
                requirement_ids
            )
        )
        ):
            raise ValueError(
                "requirement ids must be unique"
            )

        question_ids = [
            question.id
            for question
            in self.open_questions
        ]

        if (
                len(question_ids)
                != len(
            set(
                question_ids
            )
        )
        ):
            raise ValueError(
                "open-question ids "
                "must be unique"
            )

        overlap = (
                set(requirement_ids)
                & set(question_ids)
        )

        if overlap:
            raise ValueError(
                "requirement and open-question "
                "ids must not overlap"
            )

        return self