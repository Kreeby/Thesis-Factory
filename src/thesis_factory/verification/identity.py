from enum import StrEnum

from pydantic import BaseModel, ConfigDict

from thesis_factory.verification.bibliographic import (
    BibliographicComparison,
    MatchStatus,
)


class IdentityStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class IdentityVerification(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    status: IdentityStatus
    evidence: tuple[str, ...] = ()
    discrepancies: tuple[str, ...] = ()
    unknown_fields: tuple[str, ...] = ()


def verify_source_identity(
        comparison: BibliographicComparison,
) -> IdentityVerification:
    evidence: list[str] = []
    discrepancies: list[str] = []
    unknown_fields: list[str] = []

    for field_name in ("doi", "title", "publication_year", "authors"):
        status = getattr(comparison, field_name)

        if status == MatchStatus.MATCH:
            evidence.append(f"{field_name.upper()}_MATCH")
        elif status == MatchStatus.MISMATCH:
            discrepancies.append(f"{field_name.upper()}_MISMATCH")
        else:
            unknown_fields.append(field_name)

    # DOI and title are identity-defining for this first verification policy.
    if (
            comparison.doi == MatchStatus.MISMATCH
            or comparison.title == MatchStatus.MISMATCH
    ):
        status = IdentityStatus.CONFLICTING

    elif (
            comparison.doi == MatchStatus.MATCH
            and comparison.title == MatchStatus.MATCH
    ):
        status = IdentityStatus.CONFIRMED

    else:
        status = IdentityStatus.INSUFFICIENT_DATA

    return IdentityVerification(
        status=status,
        evidence=tuple(evidence),
        discrepancies=tuple(discrepancies),
        unknown_fields=tuple(unknown_fields),
    )