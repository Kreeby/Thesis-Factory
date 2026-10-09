import pytest
from pydantic import ValidationError

from thesis_factory.domain.proposal_research import (
    ResearchDimension,
)
from thesis_factory.domain.web_research import (
    ResearchLead,
    ResearchLeadSet,
)


def _lead(index: int) -> ResearchLead:
    return ResearchLead(
        lead_id=f"lead-{index}",
        dimension=ResearchDimension.DATASET,
        candidate_statement=(
            f"Candidate statement {index}."
        ),
        why_relevant=(
            "Relevant to dataset selection."
        ),
        source_citation_ids=(
            "c1",
        ),
        verification_need=(
            "Verify the source and properties."
        ),
    )


def test_research_lead_set_is_bounded() -> None:
    with pytest.raises(
        ValidationError,
    ):
        ResearchLeadSet(
            objective="Dataset research.",
            leads=tuple(
                _lead(index)
                for index in range(11)
            ),
        )


def test_research_lead_set_accepts_ten() -> None:
    lead_set = ResearchLeadSet(
        objective="Dataset research.",
        leads=tuple(
            _lead(index)
            for index in range(10)
        ),
    )

    assert len(lead_set.leads) == 10
