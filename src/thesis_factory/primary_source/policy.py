from urllib.parse import urlsplit

from thesis_factory.domain.proposal_verification import (
    ProposalVerificationTask,
    VerificationLane,
)
from thesis_factory.domain.primary_source import (
    PrimarySourceCandidate,
)


_LEGAL_HOSTS = (
    "publications.europa.eu",
    "eur-lex.europa.eu",
    "juris.curia.europa.eu",
)

_FICO_HOSTS = (
    "fico.com",
    "community.fico.com",
)

_UCI_HOSTS = (
    "archive.ics.uci.edu",
)

_KAGGLE_HOSTS = (
    "kaggle.com",
)


def source_host(
    url: str,
) -> str:
    host = (
        urlsplit(
            url
        ).hostname
        or ""
    )

    return (
        host
        .casefold()
        .removeprefix("www.")
    )


def candidate_is_authoritative(
    task: ProposalVerificationTask,
    candidate: PrimarySourceCandidate,
) -> bool:
    host = source_host(
        candidate.url
    )

    if (
        task.lane
        == VerificationLane
        .OFFICIAL_PRIMARY_WEB
    ):
        return _host_allowed(
            host,
            _LEGAL_HOSTS,
        )

    if (
        task.lane
        != VerificationLane
        .DATASET_PRIMARY
    ):
        return False

    text = " ".join(
        (
            task.requirement.question,
            task.requirement.why_needed,
        )
    ).casefold()

    if (
        "heloc" in text
        or "fico" in text
    ):
        return _host_allowed(
            host,
            _FICO_HOSTS,
        )

    if (
        "german credit" in text
        or "statlog" in text
    ):
        return _host_allowed(
            host,
            _UCI_HOSTS,
        )

    if (
        "home credit" in text
        or "kaggle" in text
    ):
        return _host_allowed(
            host,
            _KAGGLE_HOSTS,
        )

    return False


def authority_hint(
    task: ProposalVerificationTask,
) -> str:
    if (
        task.lane
        == VerificationLane
        .OFFICIAL_PRIMARY_WEB
    ):
        return (
            "Use official EU primary sources only. "
            "Prefer Publications Office/Cellar, "
            "EUR-Lex primary text, or a direct "
            "judgment document on "
            "juris.curia.europa.eu. Do not use "
            "InfoCuria list/search shells, press "
            "releases, law-firm pages, blogs, news, "
            "NGOs, or commentary as evidence."
        )

    text = " ".join(
        (
            task.requirement.question,
            task.requirement.why_needed,
        )
    ).casefold()

    if (
        "heloc" in text
        or "fico" in text
    ):
        return (
            "Find the official FICO Explainable "
            "Machine Learning Challenge or HELOC "
            "dataset documentation on FICO-controlled "
            "domains. Do not use GitHub mirrors, blogs, "
            "or papers as the primary dataset source."
        )

    if (
        "german credit" in text
        or "statlog" in text
    ):
        return (
            "Find the official UCI Machine Learning "
            "Repository page for Statlog German Credit. "
            "Do not use mirrors or secondary papers."
        )

    if (
        "home credit" in text
        or "kaggle" in text
    ):
        return (
            "Find the official Kaggle Home Credit "
            "Default Risk competition/data page. "
            "Do not use Medium posts or GitHub mirrors."
        )

    return (
        "Find the official primary dataset source "
        "owned by the dataset maintainer or canonical "
        "repository."
    )


def _host_allowed(
    host: str,
    allowed: tuple[
        str,
        ...,
    ],
) -> bool:
    return any(
        (
            host == allowed_host
            or host.endswith(
                "." + allowed_host
            )
        )
        for allowed_host
        in allowed
    )
