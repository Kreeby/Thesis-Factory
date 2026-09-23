from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from thesis_factory.domain.source import SourceRecord
from thesis_factory.research.literature_search_planning import (
    LiteratureSearchPlan,
)
from thesis_factory.workflows.literature_assessment import (
    AssessedSource,
    RelevanceAssessor,
    assess_verified_source,
)
from thesis_factory.workflows.source_verification import (
    DoiRegistry,
    SourceSearcher,
    verify_source,
)


class LiteraturePlanner(Protocol):
    def plan(
            self,
            *,
            topic: str,
    ) -> LiteratureSearchPlan:
        ...


class TopicAssessedSource(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    assessment: AssessedSource

    discovered_by_queries: tuple[str, ...] = Field(
        min_length=1,
    )


class TopicLiteratureAssessment(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    topic: str
    plan: LiteratureSearchPlan
    sources: tuple[TopicAssessedSource, ...]


def _source_key(
        source: SourceRecord,
) -> str:
    if source.doi is not None:
        return f"doi:{source.doi.casefold()}"

    return (
        f"provider:"
        f"{source.provider.casefold()}:"
        f"{source.provider_id}"
    )


def assess_literature_for_topic(
        *,
        topic: str,
        per_query_limit: int,
        planner: LiteraturePlanner,
        searcher: SourceSearcher,
        registry: DoiRegistry,
        relevance_assessor: RelevanceAssessor,
) -> TopicLiteratureAssessment:
    normalized_topic = topic.strip()

    if not normalized_topic:
        raise ValueError(
            "topic must not be empty"
        )

    if per_query_limit < 1:
        raise ValueError(
            "per_query_limit must be positive"
        )

    plan = planner.plan(
        topic=normalized_topic
    )

    discovered: dict[
        str,
        tuple[SourceRecord, list[str]],
    ] = {}

    for task in plan.tasks:
        sources = searcher.search_works(
            task.query,
            per_page=per_query_limit,
        )

        for source in sources:
            key = _source_key(source)

            existing = discovered.get(key)

            if existing is None:
                discovered[key] = (
                    source,
                    [task.query],
                )
                continue

            _, queries = existing

            if task.query not in queries:
                queries.append(task.query)

    assessed: list[TopicAssessedSource] = []

    for source, queries in discovered.values():
        verification = verify_source(
            source,
            registry=registry,
        )

        assessment = assess_verified_source(
            topic=normalized_topic,
            verification=verification,
            relevance_assessor=relevance_assessor,
        )

        assessed.append(
            TopicAssessedSource(
                assessment=assessment,
                discovered_by_queries=tuple(queries),
            )
        )

    return TopicLiteratureAssessment(
        topic=normalized_topic,
        plan=plan,
        sources=tuple(assessed),
    )