from thesis_factory.domain.source import SourceRecord
from thesis_factory.verification.bibliographic import MatchStatus
from thesis_factory.workflows.source_verification import (
    SourceVerificationStatus,
    discover_and_verify_sources,
)
from thesis_factory.verification.identity import IdentityStatus


class FakeSearcher:
    def search_works(
            self,
            query: str,
            *,
            per_page: int = 10,
    ) -> tuple[SourceRecord, ...]:
        return (
            SourceRecord(
                title="Example Paper",
                authors=("Alice Smith",),
                publication_year=2025,
                doi="10.1234/example",
                provider="openalex",
                provider_id="W1",
            ),
            SourceRecord(
                title="Paper Without DOI",
                provider="openalex",
                provider_id="W2",
            ),
        )


class FakeRegistry:
    def get_work_by_doi(
            self,
            doi: str,
    ) -> SourceRecord | None:
        if doi != "10.1234/example":
            return None

        return SourceRecord(
            title="Example Paper",
            authors=("Alice Smith",),
            publication_year=2025,
            doi="10.1234/example",
            provider="crossref",
            provider_id="10.1234/example",
        )


def test_discover_and_verify_sources() -> None:
    results = discover_and_verify_sources(
        "example",
        limit=10,
        searcher=FakeSearcher(),
        registry=FakeRegistry(),
    )

    assert len(results) == 2

    verified = results[0]

    assert verified.status == SourceVerificationStatus.COMPARED
    assert verified.comparison is not None
    assert verified.comparison.doi == MatchStatus.MATCH
    assert verified.comparison.title == MatchStatus.MATCH
    assert verified.comparison.publication_year == MatchStatus.MATCH
    assert verified.comparison.authors == MatchStatus.MATCH

    assert verified.identity is not None
    assert verified.identity.status == IdentityStatus.CONFIRMED

    no_doi = results[1]

    assert no_doi.status == SourceVerificationStatus.NO_DOI
    assert no_doi.registry_source is None
    assert no_doi.comparison is None