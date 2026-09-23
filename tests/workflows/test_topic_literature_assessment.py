from thesis_factory.domain.source import SourceRecord
from thesis_factory.research.literature_search_planning import (
    LiteratureSearchPlan,
    LiteratureSearchTask,
)
from thesis_factory.research.relevance import (
    RelevanceAssessment,
    RelevanceStatus,
)
from thesis_factory.workflows.topic_literature_assessment import (
    assess_literature_for_topic,
)


class FakePlanner:
    def plan(
            self,
            *,
            topic: str,
    ) -> LiteratureSearchPlan:
        return LiteratureSearchPlan(
            tasks=(
                LiteratureSearchTask(
                    objective="First search angle",
                    query="credit default machine learning",
                ),
                LiteratureSearchTask(
                    objective="Second search angle",
                    query="machine learning credit scoring",
                ),
            )
        )


class FakeSearcher:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def search_works(
            self,
            query: str,
            *,
            per_page: int = 10,
    ) -> tuple[SourceRecord, ...]:
        self.calls.append(query)

        shared = SourceRecord(
            title="Shared Credit Risk Paper",
            doi="10.1234/shared",
            abstract=(
                "This paper studies machine learning "
                "for credit risk."
            ),
            provider="openalex",
            provider_id="W-shared",
        )

        if query == "credit default machine learning":
            return (
                shared,
                SourceRecord(
                    title="First Unique Paper",
                    doi="10.1234/first",
                    abstract="Credit risk machine learning.",
                    provider="openalex",
                    provider_id="W-first",
                ),
            )

        return (
            shared,
            SourceRecord(
                title="Second Unique Paper",
                doi="10.1234/second",
                abstract="Credit scoring machine learning.",
                provider="openalex",
                provider_id="W-second",
            ),
        )


class FakeRegistry:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        self.calls.append(doi)

        titles = {
            "10.1234/shared": "Shared Credit Risk Paper",
            "10.1234/first": "First Unique Paper",
            "10.1234/second": "Second Unique Paper",
        }

        return SourceRecord(
            title=titles[doi],
            doi=doi,
            provider="crossref",
            provider_id=doi,
        )


class FakeRelevanceAssessor:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def assess(
            self,
            *,
            topic: str,
            source: SourceRecord,
    ) -> RelevanceAssessment:
        self.calls.append(
            source.doi or source.provider_id
        )

        return RelevanceAssessment(
            status=RelevanceStatus.RELEVANT,
            rationale="Relevant to the topic.",
        )


def test_topic_workflow_deduplicates_before_verification_and_relevance() -> None:
    searcher = FakeSearcher()
    registry = FakeRegistry()
    relevance_assessor = FakeRelevanceAssessor()

    result = assess_literature_for_topic(
        topic="machine learning credit risk",
        per_query_limit=5,
        planner=FakePlanner(),
        searcher=searcher,
        registry=registry,
        relevance_assessor=relevance_assessor,
    )

    assert len(result.plan.tasks) == 2

    # Four discovery hits were returned:
    # shared + first + shared + second.
    #
    # But only three unique papers should continue downstream.
    assert len(result.sources) == 3

    assert len(registry.calls) == 3
    assert len(relevance_assessor.calls) == 3

    shared = next(
        item
        for item in result.sources
        if (
                item.assessment
                .verification
                .discovered_source
                .doi
                == "10.1234/shared"
        )
    )

    assert shared.discovered_by_queries == (
        "credit default machine learning",
        "machine learning credit scoring",
    )


def test_topic_workflow_rejects_invalid_budget() -> None:
    try:
        assess_literature_for_topic(
            topic="machine learning credit risk",
            per_query_limit=0,
            planner=FakePlanner(),
            searcher=FakeSearcher(),
            registry=FakeRegistry(),
            relevance_assessor=FakeRelevanceAssessor(),
        )
    except ValueError as error:
        assert (
                str(error)
                == "per_query_limit must be positive"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )