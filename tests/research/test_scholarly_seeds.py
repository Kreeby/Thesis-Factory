import json

from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
    EvidenceRequirementKind,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationPlan,
    ProposalVerificationTask,
    VerificationLane,
    VerificationPriority,
)
from thesis_factory.research.scholarly_seeds import (
    load_scholarly_seed_queries,
)


def test_seed_queries_come_from_discovery_citations(
    tmp_path,
) -> None:
    artifact = {
        "packets": [
            {
                "citations": [
                    {
                        "citation_id": "c1",
                        "title": (
                            "[PDF] Exact Paper Title"
                        ),
                        "url": (
                            "https://arxiv.org/"
                            "pdf/2205.10535"
                        ),
                    }
                ]
            }
        ],
        "lead_sets": [
            {
                "leads": [
                    {
                        "lead_id": "lead-1",
                        "source_citation_ids": [
                            "c1"
                        ],
                    }
                ]
            }
        ],
    }

    path = (
        tmp_path
        / "discovery.json"
    )

    path.write_text(
        json.dumps(
            artifact
        ),
        encoding="utf-8",
    )

    plan = ProposalVerificationPlan(
        topic="Topic",
        tasks=(
            ProposalVerificationTask(
                task_id="task-1",
                requirement=(
                    EvidenceRequirement(
                        requirement_id="req-1",
                        kind=(
                            EvidenceRequirementKind
                            .LITERATURE
                        ),
                        question="Verify it.",
                        why_needed="Needed.",
                    )
                ),
                lane=(
                    VerificationLane
                    .SCHOLARLY_FULLTEXT
                ),
                priority=(
                    VerificationPriority.HIGH
                ),
                lead_ids=("lead-1",),
                rationale="Verify.",
            ),
        ),
        deferral_rationale="None.",
    )

    result = (
        load_scholarly_seed_queries(
            path,
            plan=plan,
        )
    )

    assert result["req-1"] == (
        "Exact Paper Title",
        "2205.10535",
    )
