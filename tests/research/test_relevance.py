from thesis_factory.domain.source import SourceRecord
from thesis_factory.research.relevance import (
    RelevanceAgent,
    RelevanceAssessment,
    RelevanceStatus,
)


class FakeReasoner:
    def __init__(
            self,
            result: RelevanceAssessment,
    ) -> None:
        self.result = result
        self.calls = 0

    def generate(
            self,
            *,
            system: str,
            prompt: str,
            output_model: type[RelevanceAssessment],
    ) -> RelevanceAssessment:
        self.calls += 1
        return self.result


def test_source_without_abstract_does_not_call_llm() -> None:
    reasoner = FakeReasoner(
        RelevanceAssessment(
            status=RelevanceStatus.RELEVANT,
            rationale="Unused",
        )
    )

    agent = RelevanceAgent(reasoner)

    result = agent.assess(
        topic="machine learning credit risk",
        source=SourceRecord(
            title="Example",
            provider="openalex",
            provider_id="W1",
        ),
    )

    assert result.status == RelevanceStatus.INSUFFICIENT_EVIDENCE
    assert reasoner.calls == 0


def test_source_with_abstract_is_assessed_by_reasoner() -> None:
    reasoner = FakeReasoner(
        RelevanceAssessment(
            status=RelevanceStatus.RELEVANT,
            rationale="The abstract directly studies credit risk.",
        )
    )

    agent = RelevanceAgent(reasoner)

    result = agent.assess(
        topic="machine learning credit risk",
        source=SourceRecord(
            title="Example",
            abstract="This paper studies machine learning for credit risk.",
            provider="openalex",
            provider_id="W1",
        ),
    )

    assert result.status == RelevanceStatus.RELEVANT
    assert reasoner.calls == 1