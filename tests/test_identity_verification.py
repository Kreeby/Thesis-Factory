from thesis_factory.verification.bibliographic import (
    BibliographicComparison,
    MatchStatus,
)
from thesis_factory.verification.identity import (
    IdentityStatus,
    verify_source_identity,
)


def test_identity_is_confirmed_despite_secondary_metadata_discrepancies() -> None:
    comparison = BibliographicComparison(
        left_provider="openalex",
        right_provider="crossref",
        doi=MatchStatus.MATCH,
        title=MatchStatus.MATCH,
        publication_year=MatchStatus.MISMATCH,
        authors=MatchStatus.MISMATCH,
    )

    result = verify_source_identity(comparison)

    assert result.status == IdentityStatus.CONFIRMED
    assert "DOI_MATCH" in result.evidence
    assert "TITLE_MATCH" in result.evidence
    assert "PUBLICATION_YEAR_MISMATCH" in result.discrepancies
    assert "AUTHORS_MISMATCH" in result.discrepancies


def test_title_conflict_makes_identity_conflicting() -> None:
    comparison = BibliographicComparison(
        left_provider="openalex",
        right_provider="crossref",
        doi=MatchStatus.MATCH,
        title=MatchStatus.MISMATCH,
        publication_year=MatchStatus.MATCH,
        authors=MatchStatus.MATCH,
    )

    result = verify_source_identity(comparison)

    assert result.status == IdentityStatus.CONFLICTING


def test_missing_identity_fields_are_insufficient() -> None:
    comparison = BibliographicComparison(
        left_provider="openalex",
        right_provider="crossref",
        doi=MatchStatus.UNKNOWN,
        title=MatchStatus.MATCH,
        publication_year=MatchStatus.MATCH,
        authors=MatchStatus.MATCH,
    )

    result = verify_source_identity(comparison)

    assert result.status == IdentityStatus.INSUFFICIENT_DATA
    assert "doi" in result.unknown_fields