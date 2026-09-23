from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from thesis_factory.domain.source import SourceRecord
from thesis_factory.research.relevance import RelevanceAssessment
from thesis_factory.verification.identity import IdentityStatus
from thesis_factory.workflows.source_verification import (
    DoiRegistry,
    SourceSearcher,
    SourceVerificationResult,
    discover_and_verify_sources,
)


class RelevanceAssessor(Protocol):
    def assess(
            self,
            *,
            topic: str,
            source: SourceRecord,
    ) -> RelevanceAssessment:
        ...


class AssessedSource(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    verification: SourceVerificationResult
    relevance_source: SourceRecord | None = None
    relevance: RelevanceAssessment | None = None


class LiteratureQueryResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    topic: str = Field(min_length=1)
    query: str = Field(min_length=1)
    sources: tuple[AssessedSource, ...]


def assess_literature_for_query(
        *,
        topic: str,
        query: str,
        limit: int,
        searcher: SourceSearcher,
        registry: DoiRegistry,
        relevance_assessor: RelevanceAssessor,
) -> LiteratureQueryResult:
    if not topic.strip():
        raise ValueError("topic must not be empty")

    if not query.strip():
        raise ValueError("query must not be empty")

    verified_sources = discover_and_verify_sources(
        query,
        limit=limit,
        searcher=searcher,
        registry=registry,
    )

    assessed_sources: list[AssessedSource] = []

    for verification in verified_sources:
        identity = verification.identity

        if (
                identity is None
                or identity.status != IdentityStatus.CONFIRMED
        ):
            assessed_sources.append(
                AssessedSource(
                    verification=verification,
                )
            )
            continue

        relevance_source = _select_relevance_source(
            verification
        )

        relevance = relevance_assessor.assess(
            topic=topic,
            source=relevance_source,
        )

        assessed_sources.append(
            AssessedSource(
                verification=verification,
                relevance_source=relevance_source,
                relevance=relevance,
            )
        )

    return LiteratureQueryResult(
        topic=topic.strip(),
        query=query.strip(),
        sources=tuple(assessed_sources),
    )

def _select_relevance_source(
        verification: SourceVerificationResult,
) -> SourceRecord:
    discovered = verification.discovered_source

    if discovered.abstract and discovered.abstract.strip():
        return discovered

    registry = verification.registry_source

    if (
            registry is not None
            and registry.abstract
            and registry.abstract.strip()
    ):
        return registry

    return discovered