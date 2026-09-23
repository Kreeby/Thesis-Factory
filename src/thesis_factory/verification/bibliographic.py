import re
from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from thesis_factory.domain.source import SourceRecord


class MatchStatus(StrEnum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNKNOWN = "UNKNOWN"


class BibliographicComparison(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    left_provider: str
    right_provider: str

    doi: MatchStatus
    title: MatchStatus
    publication_year: MatchStatus
    authors: MatchStatus


def compare_bibliographic_metadata(
        left: SourceRecord,
        right: SourceRecord,
) -> BibliographicComparison:
    return BibliographicComparison(
        left_provider=left.provider,
        right_provider=right.provider,
        doi=_compare_optional(
            left.doi,
            right.doi,
        ),
        title=_compare_titles(
            left.title,
            right.title,
        ),
        publication_year=_compare_optional(
            left.publication_year,
            right.publication_year,
        ),
        authors=_compare_authors(
            left.authors,
            right.authors,
        ),
    )


def _compare_optional(
        left: object | None,
        right: object | None,
) -> MatchStatus:
    if left is None or right is None:
        return MatchStatus.UNKNOWN

    return (
        MatchStatus.MATCH
        if left == right
        else MatchStatus.MISMATCH
    )


def _compare_titles(
        left: str,
        right: str,
) -> MatchStatus:
    return (
        MatchStatus.MATCH
        if _normalize_text(left) == _normalize_text(right)
        else MatchStatus.MISMATCH
    )


def _compare_authors(
        left: tuple[str, ...],
        right: tuple[str, ...],
) -> MatchStatus:
    if not left or not right:
        return MatchStatus.UNKNOWN

    normalized_left = {
        _normalize_text(author)
        for author in left
    }

    normalized_right = {
        _normalize_text(author)
        for author in right
    }

    return (
        MatchStatus.MATCH
        if normalized_left == normalized_right
        else MatchStatus.MISMATCH
    )


def _normalize_text(value: str) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        "",
        value.casefold(),
    )