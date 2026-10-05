from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
)


class VerificationLane(StrEnum):
    SCHOLARLY_FULLTEXT = "SCHOLARLY_FULLTEXT"
    OFFICIAL_PRIMARY_WEB = "OFFICIAL_PRIMARY_WEB"
    DATASET_PRIMARY = "DATASET_PRIMARY"


class VerificationPriority(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"


class ProposalVerificationTask(BaseModel):
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
    lane: VerificationLane
    priority: VerificationPriority

    lead_ids: tuple[str, ...] = Field(
        min_length=1,
        max_length=12,
    )

    rationale: str = Field(
        min_length=1,
        max_length=1000,
    )

    @model_validator(mode="after")
    def validate_unique_lead_ids(self) -> Self:
        if len(self.lead_ids) != len(set(self.lead_ids)):
            raise ValueError(
                "verification task lead ids must be unique"
            )
        return self


class ProposalVerificationPlan(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    topic: str = Field(
        min_length=1,
        max_length=500,
    )

    tasks: tuple[ProposalVerificationTask, ...] = Field(
        min_length=1,
        max_length=18,
    )

    deferred_lead_ids: tuple[str, ...] = Field(
        default=(),
        max_length=100,
    )

    deferral_rationale: str = Field(
        min_length=1,
        max_length=1500,
    )

    @model_validator(mode="after")
    def validate_plan_internal_uniqueness(self) -> Self:
        task_ids = [task.task_id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            raise ValueError(
                "verification task ids must be unique"
            )

        requirement_ids = [
            task.requirement.requirement_id
            for task in self.tasks
        ]
        if len(requirement_ids) != len(set(requirement_ids)):
            raise ValueError(
                "verification requirement ids must be unique"
            )

        task_lead_ids = [
            lead_id
            for task in self.tasks
            for lead_id in task.lead_ids
        ]
        if len(task_lead_ids) != len(set(task_lead_ids)):
            raise ValueError(
                "a discovery lead may belong to only one verification task"
            )

        if len(self.deferred_lead_ids) != len(set(self.deferred_lead_ids)):
            raise ValueError(
                "deferred lead ids must be unique"
            )

        if set(task_lead_ids) & set(self.deferred_lead_ids):
            raise ValueError(
                "lead ids cannot be both scheduled and deferred"
            )

        return self
