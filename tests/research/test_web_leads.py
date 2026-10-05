import pytest

from thesis_factory.domain.proposal_research import (
    ResearchDimension,
)
from thesis_factory.domain.web_research import (
    ResearchLead,
    ResearchLeadSet,
    WebCitation,
    WebResearchPacket,
)
from thesis_factory.research.web_leads import (
    ResearchLeadError,
    WebResearchLeadExtractor,
    validate_research_leads,
)


def _packet() -> WebResearchPacket:
    return WebResearchPacket(
        objective="Find candidate datasets.",
        narrative="A dataset source was found.",
        citations=(
            WebCitation(
                citation_id="c1",
                url="https://example.org/dataset",
                title="Dataset",
                cited_text="Official dataset page.",
            ),
        ),
    )


def _leads(
    citation_id="c1",
) -> ResearchLeadSet:
    return ResearchLeadSet(
        objective="Find candidate datasets.",
        leads=(
            ResearchLead(
                lead_id="dataset-1",
                dimension=ResearchDimension.DATASET,
                candidate_statement=(
                    "Candidate dataset may be "
                    "suitable for evaluation."
                ),
                why_relevant=(
                    "It appears related to "
                    "the target task."
                ),
                source_citation_ids=(
                    citation_id,
                ),
                verification_need=(
                    "Verify provenance, licence, "
                    "target semantics, scale, "
                    "features, and availability."
                ),
            ),
        ),
    )


class FakeReasoner:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def generate(self, **kwargs):
        self.calls.append(
            kwargs
        )
        return self.result


def test_lead_extractor_keeps_discovery_unverified() -> None:
    reasoner = FakeReasoner(
        _leads()
    )

    extractor = (
        WebResearchLeadExtractor(
            reasoner
        )
    )

    result = extractor.extract(
        packet=_packet()
    )

    assert (
        result.leads[0].state.value
        == "DISCOVERED"
    )

    assert (
        "NOT verified evidence"
        in reasoner.calls[0]["system"]
    )

    assert (
        "citation_id"
        in reasoner.calls[0]["prompt"]
    )


def test_rejects_unknown_citation_id() -> None:
    with pytest.raises(
        ResearchLeadError,
        match="citation id not present",
    ):
        validate_research_leads(
            _leads("c999"),
            packet=_packet(),
        )
