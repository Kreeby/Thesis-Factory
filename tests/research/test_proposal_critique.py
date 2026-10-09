from thesis_factory.domain.evidence_acquisition import (
    EvidenceSupportStatus,
    VerifiedEvidenceResult,
)
from thesis_factory.domain.proposal_research import (
    CritiqueVerdict,
    ProposalCritique,
    ProposalResearchDraft,
    ResearchDimension,
    ResearchFinding,
    ResearchFindingState,
)
from thesis_factory.research.proposal_critique import (
    ProposalCritic,
)


class FakeReasoner:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def generate(
        self,
        *,
        system,
        prompt,
        output_model,
    ):
        self.calls.append(system)
        return self.result


def test_critic_is_independent_and_adversarial() -> None:
    critique = ProposalCritique(
        verdict=CritiqueVerdict.PASS,
        summary="No unsupported claims remain.",
    )

    reasoner = FakeReasoner(
        critique
    )

    critic = ProposalCritic(
        reasoner
    )

    draft = ProposalResearchDraft(
        approved_topic="Topic",
        findings=(
            ResearchFinding(
                finding_id="f1",
                dimension=ResearchDimension.RISK,
                statement="A limitation exists.",
                rationale="Derived from evidence.",
                state=ResearchFindingState.DERIVED,
                supporting_requirement_ids=("r1",),
            ),
        ),
    )

    evidence = (
        VerifiedEvidenceResult(
            requirement_id="r1",
            status=EvidenceSupportStatus.SUPPORTED,
            rationale="Supported.",
            evidence=(),
        ),
    )

    result = critic.critique(
        draft=draft,
        evidence_results=evidence,
    )

    assert result == critique
    assert (
        "unsupported novelty"
        in reasoner.calls[0]
    )
