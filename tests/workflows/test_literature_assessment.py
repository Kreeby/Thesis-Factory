from thesis_factory.domain.source import SourceRecord
from thesis_factory.research.relevance import (
    RelevanceAssessment,
    RelevanceStatus,
)
from thesis_factory.workflows.literature_assessment import (
    assess_literature_for_query,
)
from thesis_factory.workflows.source_verification import (
    SourceVerificationStatus,
)


class FakeSearcher:
    def __init__(self) -> None:
        self.queries: list[tuple[str, int]] = []

    def search_works(
            self,
            query: str,
            *,
            per_page: int = 10,
    ) -> tuple[SourceRecord, ...]:
        self.queries.append((query, per_page))

        return (
            SourceRecord(
                title="Relevant Credit Risk Paper",
                authors=("Alice Smith",),
                publication_year=2025,
                doi="10.1234/relevant",
                abstract=(
                    "This paper studies machine learning "
                    "for consumer credit risk."
                ),
                provider="openalex",
                provider_id="W1",
            ),
            SourceRecord(
                title="Paper Without DOI",
                abstract="This paper also discusses credit risk.",
                provider="openalex",
                provider_id="W2",
            ),
            SourceRecord(
                title="Unregistered Paper",
                doi="10.1234/missing",
                abstract="This paper discusses credit risk.",
                provider="openalex",
                provider_id="W3",
            ),
        )


class FakeRegistry:
    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        if doi == "10.1234/relevant":
            return SourceRecord(
                title="Relevant Credit Risk Paper",
                authors=("Alice Smith",),
                publication_year=2025,
                doi="10.1234/relevant",
                provider="crossref",
                provider_id="10.1234/relevant",
            )

        return None


class FakeRelevanceAssessor:
    def __init__(self) -> None:
        self.calls: list[tuple[str, SourceRecord]] = []

    def assess(
            self,
            *,
            topic: str,
            source: SourceRecord,
    ) -> RelevanceAssessment:
        self.calls.append((topic, source))

        return RelevanceAssessment(
            status=RelevanceStatus.RELEVANT,
            rationale="The paper directly addresses the topic.",
        )

class FakeSearcherWithoutAbstract:
    def search_works(
            self,
            query: str,
            *,
            per_page: int = 10,
    ) -> tuple[SourceRecord, ...]:
        return (
            SourceRecord(
                title="Consumer Credit Risk Paper",
                doi="10.1234/fallback",
                provider="openalex",
                provider_id="W-fallback",
            ),
        )


class FakeRegistryWithAbstract:
    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        return SourceRecord(
            title="Consumer Credit Risk Paper",
            doi="10.1234/fallback",
            abstract=(
                "This study applies machine learning "
                "to consumer credit default prediction."
            ),
            provider="crossref",
            provider_id="10.1234/fallback",
        )


def test_assess_literature_for_query_composes_pipeline() -> None:
    searcher = FakeSearcher()
    registry = FakeRegistry()
    relevance_assessor = FakeRelevanceAssessor()

    result = assess_literature_for_query(
        topic="machine learning credit risk",
        query="consumer default prediction machine learning",
        limit=3,
        searcher=searcher,
        registry=registry,
        relevance_assessor=relevance_assessor,
    )

    assert result.topic == "machine learning credit risk"
    assert result.query == "consumer default prediction machine learning"
    assert len(result.sources) == 3

    # Discovery operates on the search query, not the topic.
    assert searcher.queries == [
        ("consumer default prediction machine learning", 3)
    ]

    confirmed = result.sources[0]

    assert (
            confirmed.verification.status
            == SourceVerificationStatus.COMPARED
    )
    assert confirmed.verification.identity is not None
    assert confirmed.relevance is not None
    assert confirmed.relevance.status == RelevanceStatus.RELEVANT

    no_doi = result.sources[1]

    assert (
            no_doi.verification.status
            == SourceVerificationStatus.NO_DOI
    )
    assert no_doi.relevance is None

    not_found = result.sources[2]

    assert (
            not_found.verification.status
            == SourceVerificationStatus.NOT_FOUND_IN_REGISTRY
    )
    assert not_found.relevance is None

    # Relevance is evaluated only for the confirmed source,
    # and against the original topic rather than the search query.
    assert len(relevance_assessor.calls) == 1

    assessed_topic, assessed_source = relevance_assessor.calls[0]

    assert assessed_topic == "machine learning credit risk"
    assert assessed_source.provider_id == "W1"


def test_assess_literature_for_query_rejects_empty_topic() -> None:
    try:
        assess_literature_for_query(
            topic="   ",
            query="credit risk",
            limit=3,
            searcher=FakeSearcher(),
            registry=FakeRegistry(),
            relevance_assessor=FakeRelevanceAssessor(),
        )
    except ValueError as error:
        assert str(error) == "topic must not be empty"
    else:
        raise AssertionError("Expected ValueError")


def test_assess_literature_for_query_rejects_empty_query() -> None:
    try:
        assess_literature_for_query(
            topic="machine learning credit risk",
            query="   ",
            limit=3,
            searcher=FakeSearcher(),
            registry=FakeRegistry(),
            relevance_assessor=FakeRelevanceAssessor(),
        )
    except ValueError as error:
        assert str(error) == "query must not be empty"
    else:
        raise AssertionError("Expected ValueError")

def test_crossref_abstract_is_used_when_discovery_abstract_is_missing() -> None:
    relevance_assessor = FakeRelevanceAssessor()

    result = assess_literature_for_query(
        topic="machine learning credit risk",
        query="consumer default prediction",
        limit=1,
        searcher=FakeSearcherWithoutAbstract(),
        registry=FakeRegistryWithAbstract(),
        relevance_assessor=relevance_assessor,
    )

    assessed = result.sources[0]

    assert assessed.relevance_source is not None
    assert assessed.relevance_source.provider == "crossref"
    assert assessed.relevance_source.abstract is not None

    assert len(relevance_assessor.calls) == 1

    _, source = relevance_assessor.calls[0]

    assert source.provider == "crossref"
    assert (
            source.abstract
            == (
                "This study applies machine learning "
                "to consumer credit default prediction."
            )
    )

def test_discovery_abstract_is_preferred_over_registry_abstract() -> None:
    class Searcher:
        def search_works(
                self,
                query: str,
                *,
                per_page: int = 10,
        ) -> tuple[SourceRecord, ...]:
            return (
                SourceRecord(
                    title="Credit Risk Paper",
                    doi="10.1234/preference",
                    abstract="OpenAlex abstract.",
                    provider="openalex",
                    provider_id="W-preference",
                ),
            )

    class Registry:
        def get_work_by_doi(
                self,
                doi: str,
        ) -> SourceRecord | None:
            return SourceRecord(
                title="Credit Risk Paper",
                doi="10.1234/preference",
                abstract="Crossref abstract.",
                provider="crossref",
                provider_id="10.1234/preference",
            )

    relevance_assessor = FakeRelevanceAssessor()

    result = assess_literature_for_query(
        topic="machine learning credit risk",
        query="credit risk",
        limit=1,
        searcher=Searcher(),
        registry=Registry(),
        relevance_assessor=relevance_assessor,
    )

    assessed = result.sources[0]

    assert assessed.relevance_source is not None
    assert assessed.relevance_source.provider == "openalex"
    assert assessed.relevance_source.abstract == "OpenAlex abstract."