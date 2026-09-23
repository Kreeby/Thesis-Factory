from thesis_factory.domain.source import SourceRecord
from thesis_factory.verification.bibliographic import (
    MatchStatus,
    compare_bibliographic_metadata,
)


def test_matching_bibliographic_metadata() -> None:
    openalex = SourceRecord(
        title="Consumer credit-risk models via machine-learning algorithms",
        authors=(
            "Amir E. Khandani",
            "Adlar J. Kim",
            "Andrew W. Lo",
        ),
        publication_year=2010,
        doi="10.1016/j.jbankfin.2010.06.001",
        provider="openalex",
        provider_id="W3121588992",
    )

    crossref = SourceRecord(
        title="Consumer Credit-Risk Models Via Machine-Learning Algorithms",
        authors=(
            "Amir E. Khandani",
            "Adlar J. Kim",
            "Andrew W. Lo",
        ),
        publication_year=2010,
        doi="https://doi.org/10.1016/j.jbankfin.2010.06.001",
        provider="crossref",
        provider_id="10.1016/j.jbankfin.2010.06.001",
    )

    result = compare_bibliographic_metadata(
        openalex,
        crossref,
    )

    assert result.doi == MatchStatus.MATCH
    assert result.title == MatchStatus.MATCH
    assert result.publication_year == MatchStatus.MATCH
    assert result.authors == MatchStatus.MATCH


def test_missing_metadata_is_unknown_not_mismatch() -> None:
    left = SourceRecord(
        title="Example Paper",
        provider="openalex",
        provider_id="W1",
    )

    right = SourceRecord(
        title="Example Paper",
        publication_year=2025,
        provider="crossref",
        provider_id="10.1234/example",
    )

    result = compare_bibliographic_metadata(
        left,
        right,
    )

    assert result.doi == MatchStatus.UNKNOWN
    assert result.publication_year == MatchStatus.UNKNOWN
    assert result.authors == MatchStatus.UNKNOWN