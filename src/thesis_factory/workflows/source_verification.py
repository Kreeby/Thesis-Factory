from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from thesis_factory.domain.source import SourceRecord
from thesis_factory.verification.bibliographic import (
    BibliographicComparison,
    compare_bibliographic_metadata,
)
from thesis_factory.verification.identity import (
    IdentityVerification,
    verify_source_identity,
)


class SourceVerificationStatus(StrEnum):
    COMPARED = "COMPARED"
    NO_DOI = "NO_DOI"
    NOT_FOUND_IN_CROSSREF = "NOT_FOUND_IN_CROSSREF"


class SourceVerificationResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    discovered_source: SourceRecord
    registry_source: SourceRecord | None = None
    comparison: BibliographicComparison | None = None
    status: SourceVerificationStatus
    identity: IdentityVerification | None = None


class SourceSearcher(Protocol):
    def search_works(
            self,
            query: str,
            *,
            per_page: int = 10,
    ) -> tuple[SourceRecord, ...]:
        ...


class DoiRegistry(Protocol):
    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        ...


def discover_and_verify_sources(
        query: str,
        *,
        limit: int,
        searcher: SourceSearcher,
        registry: DoiRegistry,
) -> tuple[SourceVerificationResult, ...]:
    discovered = searcher.search_works(
        query,
        per_page=limit,
    )

    results: list[SourceVerificationResult] = []

    for source in discovered:
        if source.doi is None:
            results.append(
                SourceVerificationResult(
                    discovered_source=source,
                    status=SourceVerificationStatus.NO_DOI,
                )
            )
            continue

        registry_source = registry.get_work_by_doi(source.doi)

        if registry_source is None:
            results.append(
                SourceVerificationResult(
                    discovered_source=source,
                    status=SourceVerificationStatus.NOT_FOUND_IN_CROSSREF,
                )
            )
            continue

        comparison = compare_bibliographic_metadata(
            source,
            registry_source,
        )

        identity = verify_source_identity(comparison)

        results.append(
            SourceVerificationResult(
                discovered_source=source,
                registry_source=registry_source,
                comparison=comparison,
                identity=identity,
                status=SourceVerificationStatus.COMPARED,
            )
        )

    return tuple(results)