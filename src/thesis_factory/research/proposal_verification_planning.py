import re
from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field

from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.domain.proposal_research import (
    ResearchDimension,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationPlan,
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.domain.web_research import (
    ResearchLead,
)


class ProposalVerificationPlanningError(ValueError):
    pass


class DiscoveryObjective(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    objective: str = Field(
        min_length=1,
        max_length=1000,
    )
    leads: tuple[ResearchLead, ...] = Field(
        min_length=1,
        max_length=20,
    )


class DiscoveryArtifact(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    topic: str = Field(
        min_length=1,
        max_length=500,
    )
    objectives: tuple[DiscoveryObjective, ...] = Field(
        min_length=1,
        max_length=20,
    )


_BUCKET_QUOTAS = {
    "LEGAL": 5,
    "DATASET": 3,
    "BASELINE": 4,
    "METHOD": 3,
    "METRIC": 3,
}

_SCHOLARLY_CLAIM_PATTERN = re.compile(
    r"\b(?:paper|study|review|survey|benchmark|literature|authors?)\b",
    flags=re.IGNORECASE,
)

_LEGAL_PATTERN = re.compile(
    r"\b(?:"
    r"gdpr|cjeu|schufa|ccd2|consumer credit directive|"
    r"ai act|annex iii|article\s+\d+|art\.\s*\d+|"
    r"directive\s*\(?(?:eu)?|regulation\s*\(?(?:eu)?|"
    r"cfpb|ecoa|regulation b|adverse[- ]action|"
    r"court|judgment|statute|regulator|legal basis"
    r")\b",
    flags=re.IGNORECASE,
)


class DeterministicProposalVerificationPlanner:
    """Selects a bounded, proposal-critical verification frontier.

    The discovery model already produced ordered leads. This planner does
    not ask another LLM to summarize them. It preserves that ordering while
    software enforces evidence-family coverage and a hard task budget.
    """

    def plan(
        self,
        *,
        artifact: DiscoveryArtifact,
    ) -> ProposalVerificationPlan:
        ordered_leads = tuple(
            lead
            for objective in artifact.objectives
            for lead in objective.leads
        )

        lead_ids = [lead.lead_id for lead in ordered_leads]
        if len(lead_ids) != len(set(lead_ids)):
            raise ProposalVerificationPlanningError(
                "discovery lead ids must be globally unique"
            )

        buckets: dict[str, list[ResearchLead]] = defaultdict(list)
        for lead in ordered_leads:
            bucket = _verification_bucket(lead)
            if bucket is not None:
                buckets[bucket].append(lead)

        selected: list[ResearchLead] = []
        selected_ids: set[str] = set()

        for bucket, quota in _BUCKET_QUOTAS.items():
            candidates = sorted(
                buckets.get(bucket, []),
                key=_selection_sort_key,
            )
            for lead in candidates[:quota]:
                if lead.lead_id in selected_ids:
                    continue
                selected.append(lead)
                selected_ids.add(lead.lead_id)

        # If a bucket under-fills, use the remaining budget for the next
        # highest-priority discovery leads, while preserving boundedness.
        hard_limit = sum(_BUCKET_QUOTAS.values())
        if len(selected) < hard_limit:
            remaining = sorted(
                (
                    lead
                    for lead in ordered_leads
                    if lead.lead_id not in selected_ids
                ),
                key=_selection_sort_key,
            )
            for lead in remaining:
                if len(selected) >= hard_limit:
                    break
                selected.append(lead)
                selected_ids.add(lead.lead_id)

        tasks = tuple(
            _task_from_lead(lead)
            for lead in selected
        )

        deferred = tuple(
            lead.lead_id
            for lead in ordered_leads
            if lead.lead_id not in selected_ids
        )

        plan = ProposalVerificationPlan(
            topic=artifact.topic,
            tasks=tasks,
            deferred_lead_ids=deferred,
            deferral_rationale=(
                "The deterministic proposal frontier verifies up to 18 "
                "ordered discovery leads while reserving coverage for "
                "legal grounding, competing datasets, predictive baselines, "
                "methods, and evaluation metrics. Remaining leads stay "
                "DISCOVERED and may be promoted after the first verification "
                "and critic pass."
            ),
        )

        validate_verification_plan(
            plan,
            artifact=artifact,
        )
        return plan


def validate_verification_plan(
    plan: ProposalVerificationPlan,
    *,
    artifact: DiscoveryArtifact,
) -> None:
    if plan.topic != artifact.topic:
        raise ProposalVerificationPlanningError(
            "verification plan topic does not match discovery artifact"
        )

    known = {
        lead.lead_id
        for objective in artifact.objectives
        for lead in objective.leads
    }
    scheduled = {
        lead_id
        for task in plan.tasks
        for lead_id in task.lead_ids
    }
    deferred = set(plan.deferred_lead_ids)

    if (scheduled | deferred) - known:
        raise ProposalVerificationPlanningError(
            "verification plan references unknown discovery lead ids"
        )

    if known - (scheduled | deferred):
        raise ProposalVerificationPlanningError(
            "verification plan does not account for every discovery lead"
        )


def _verification_bucket(lead: ResearchLead) -> str | None:
    lane = _lane_for_lead(lead)
    if lane == VerificationLane.OFFICIAL_PRIMARY_WEB:
        return "LEGAL"
    if lane == VerificationLane.DATASET_PRIMARY:
        return "DATASET"
    if lead.dimension == ResearchDimension.BASELINE:
        return "BASELINE"
    if lead.dimension == ResearchDimension.METHOD:
        return "METHOD"
    if lead.dimension == ResearchDimension.METRIC:
        return "METRIC"
    return None


def _selection_sort_key(lead: ResearchLead) -> int:
    priority_rank = {
        VerificationPriority.CRITICAL: 0,
        VerificationPriority.HIGH: 1,
        VerificationPriority.NORMAL: 2,
    }
    return priority_rank[_priority_for_lead(lead)]


def _task_from_lead(lead: ResearchLead) -> ProposalVerificationTask:
    lane = _lane_for_lead(lead)
    kind = _requirement_kind(lead, lane=lane)

    return ProposalVerificationTask(
        task_id=f"verify-{lead.lead_id}",
        requirement=EvidenceRequirement(
            requirement_id=f"req-{lead.lead_id}",
            kind=kind,
            question=lead.candidate_statement,
            why_needed=lead.verification_need,
        ),
        lane=lane,
        priority=_priority_for_lead(lead),
        lead_ids=(lead.lead_id,),
        rationale=lead.why_relevant,
    )


def _lane_for_lead(lead: ResearchLead) -> VerificationLane:
    if lead.dimension == ResearchDimension.DATASET:
        return VerificationLane.DATASET_PRIMARY

    text = " ".join(
        (
            lead.candidate_statement,
            lead.why_relevant,
            lead.verification_need,
        )
    )
    if (
        lead.dimension != ResearchDimension.PROBLEM
        and _SCHOLARLY_CLAIM_PATTERN.search(
            lead.candidate_statement
        )
    ):
        return VerificationLane.SCHOLARLY_FULLTEXT

    if _LEGAL_PATTERN.search(text):
        return VerificationLane.OFFICIAL_PRIMARY_WEB

    return VerificationLane.SCHOLARLY_FULLTEXT


def _priority_for_lead(lead: ResearchLead) -> VerificationPriority:
    if lead.dimension in {
        ResearchDimension.PROBLEM,
        ResearchDimension.RESEARCH_GAP,
        ResearchDimension.RESEARCH_QUESTION,
        ResearchDimension.DATASET,
    }:
        return VerificationPriority.CRITICAL

    if lead.dimension in {
        ResearchDimension.BASELINE,
        ResearchDimension.METHOD,
        ResearchDimension.METRIC,
        ResearchDimension.FEASIBILITY,
        ResearchDimension.CONTRIBUTION,
    }:
        return VerificationPriority.HIGH

    return VerificationPriority.NORMAL


def _requirement_kind(
    lead: ResearchLead,
    *,
    lane: VerificationLane,
) -> EvidenceRequirementKind:
    if lane == VerificationLane.OFFICIAL_PRIMARY_WEB:
        return EvidenceRequirementKind.LEGAL
    if lane == VerificationLane.DATASET_PRIMARY:
        return EvidenceRequirementKind.DATASET

    mapping = {
        ResearchDimension.BASELINE: EvidenceRequirementKind.BASELINE,
        ResearchDimension.METHOD: EvidenceRequirementKind.METHOD,
        ResearchDimension.METRIC: EvidenceRequirementKind.METRIC,
        ResearchDimension.FEASIBILITY: EvidenceRequirementKind.FEASIBILITY,
        ResearchDimension.CONTRIBUTION: EvidenceRequirementKind.CONTRIBUTION,
    }
    return mapping.get(
        lead.dimension,
        EvidenceRequirementKind.LITERATURE,
    )
