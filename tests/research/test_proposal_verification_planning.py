import pytest

from thesis_factory.domain.proposal_research import (
    ResearchDimension,
)
from thesis_factory.domain.proposal_verification import (
    VerificationLane,
)
from thesis_factory.domain.web_research import (
    ResearchLead,
)
from thesis_factory.research.proposal_verification_planning import (
    DeterministicProposalVerificationPlanner,
    DiscoveryArtifact,
    DiscoveryObjective,
    ProposalVerificationPlanningError,
    validate_verification_plan,
)


def _lead(
    lead_id: str,
    *,
    dimension: ResearchDimension,
    statement: str,
) -> ResearchLead:
    return ResearchLead(
        lead_id=lead_id,
        dimension=dimension,
        candidate_statement=statement,
        why_relevant="Relevant to the proposal.",
        source_citation_ids=("c1",),
        verification_need="Verify against authoritative evidence.",
    )


def test_deterministic_planner_requires_no_reasoner() -> None:
    artifact = DiscoveryArtifact(
        topic="Topic",
        objectives=(
            DiscoveryObjective(
                objective="Objective",
                leads=(
                    _lead(
                        "legal-1",
                        dimension=ResearchDimension.PROBLEM,
                        statement=(
                            "Verify whether GDPR Article 22 "
                            "applies to the decision."
                        ),
                    ),
                    _lead(
                        "dataset-1",
                        dimension=ResearchDimension.DATASET,
                        statement="Verify the candidate dataset.",
                    ),
                ),
            ),
        ),
    )

    plan = (
        DeterministicProposalVerificationPlanner()
        .plan(artifact=artifact)
    )

    assert len(plan.tasks) == 2
    assert plan.tasks[0].lane == (
        VerificationLane.OFFICIAL_PRIMARY_WEB
    )
    assert plan.tasks[1].lane == (
        VerificationLane.DATASET_PRIMARY
    )


def test_scholarly_gap_claim_is_not_forced_to_legal_lane() -> None:
    artifact = DiscoveryArtifact(
        topic="Topic",
        objectives=(
            DiscoveryObjective(
                objective="Objective",
                leads=(
                    _lead(
                        "gap-1",
                        dimension=ResearchDimension.RESEARCH_GAP,
                        statement=(
                            "Verify the claim in the ACM paper "
                            "that CCD2 Article 18 is ambiguous."
                        ),
                    ),
                ),
            ),
        ),
    )

    plan = (
        DeterministicProposalVerificationPlanner()
        .plan(artifact=artifact)
    )

    assert plan.tasks[0].lane == (
        VerificationLane.SCHOLARLY_FULLTEXT
    )


def test_plan_accounts_for_every_lead() -> None:
    leads = tuple(
        _lead(
            f"metric-{index}",
            dimension=ResearchDimension.METRIC,
            statement=f"Verify metric {index}.",
        )
        for index in range(5)
    )
    artifact = DiscoveryArtifact(
        topic="Topic",
        objectives=(
            DiscoveryObjective(
                objective="Objective",
                leads=leads,
            ),
        ),
    )

    plan = (
        DeterministicProposalVerificationPlanner()
        .plan(artifact=artifact)
    )

    scheduled = {
        lead_id
        for task in plan.tasks
        for lead_id in task.lead_ids
    }
    deferred = set(plan.deferred_lead_ids)

    assert scheduled | deferred == {
        lead.lead_id
        for lead in leads
    }


def test_validator_rejects_topic_mismatch() -> None:
    artifact = DiscoveryArtifact(
        topic="Topic",
        objectives=(
            DiscoveryObjective(
                objective="Objective",
                leads=(
                    _lead(
                        "dataset-1",
                        dimension=ResearchDimension.DATASET,
                        statement="Verify dataset.",
                    ),
                ),
            ),
        ),
    )

    plan = (
        DeterministicProposalVerificationPlanner()
        .plan(artifact=artifact)
    )
    mismatched = plan.model_copy(
        update={"topic": "Other topic"}
    )

    with pytest.raises(
        ProposalVerificationPlanningError,
        match="topic does not match",
    ):
        validate_verification_plan(
            mismatched,
            artifact=artifact,
        )
