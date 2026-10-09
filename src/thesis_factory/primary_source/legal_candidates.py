import re

from thesis_factory.domain.primary_source import (
    PrimarySourceCandidate,
)
from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
)


_CASE_PATTERN = re.compile(
    r"\bC[\-\u2010\u2011\u2012\u2013\u2014 ]?"
    r"(?P<number>\d{1,4})/"
    r"(?P<year>\d{2,4})\b",
    flags=re.IGNORECASE,
)

_INSTRUMENT_PATTERN = re.compile(
    r"\b(?P<kind>Regulation|Directive)"
    r"(?:\s*\(EU\))?"
    r"\s+(?P<year>20\d{2})/"
    r"(?P<number>\d{1,4})\b",
    flags=re.IGNORECASE,
)

_ALIAS_CELEX = {
    "gdpr": "32016R0679",
    "ai act": "32024R1689",
    "ccd2": "32023L2225",
}


def deterministic_legal_candidates(
    task: ProposalVerificationTask,
) -> tuple[
    PrimarySourceCandidate,
    ...,
]:
    if (
        task.lane
        != VerificationLane
        .OFFICIAL_PRIMARY_WEB
    ):
        return ()

    text = " ".join(
        (
            task.requirement.question,
            task.requirement.why_needed,
        )
    )

    celex_ids: list[str] = []

    for match in _CASE_PATTERN.finditer(
        text
    ):
        year = _four_digit_year(
            match.group(
                "year"
            )
        )

        number = int(
            match.group(
                "number"
            )
        )

        celex_ids.append(
            f"6{year}CJ{number:04d}"
        )

    for match in _INSTRUMENT_PATTERN.finditer(
        text
    ):
        kind = (
            match.group(
                "kind"
            )
            .casefold()
        )

        year = match.group(
            "year"
        )

        number = int(
            match.group(
                "number"
            )
        )

        letter = (
            "R"
            if kind == "regulation"
            else "L"
        )

        celex_ids.append(
            f"3{year}{letter}{number:04d}"
        )

    lower = text.casefold()

    for alias, celex in (
        _ALIAS_CELEX.items()
    ):
        if alias in lower:
            celex_ids.append(
                celex
            )

    unique_celex = tuple(
        dict.fromkeys(
            celex_ids
        )
    )

    candidates: list[
        PrimarySourceCandidate
    ] = []

    for celex in unique_celex:
        candidates.extend(
            (
                PrimarySourceCandidate(
                    url=(
                        "https://publications.europa.eu/"
                        f"resource/celex/{celex}"
                        "?language=eng"
                    ),
                    title=(
                        "Publications Office primary "
                        f"content {celex}"
                    ),
                ),
                PrimarySourceCandidate(
                    url=(
                        "https://eur-lex.europa.eu/"
                        "legal-content/EN/TXT/"
                        f"?uri=CELEX:{celex}"
                    ),
                    title=(
                        f"EUR-Lex text view {celex}"
                    ),
                ),
            )
        )

    return tuple(
        candidates
    )


def _four_digit_year(
    value: str,
) -> str:
    if len(value) == 4:
        return value

    year = int(
        value
    )

    return str(
        2000 + year
        if year <= 69
        else 1900 + year
    )
