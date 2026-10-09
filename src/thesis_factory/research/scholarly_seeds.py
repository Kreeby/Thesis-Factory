import json
import re
from pathlib import Path

from thesis_factory.domain.proposal_verification import (
    ProposalVerificationPlan,
    VerificationLane,
)


class ScholarlySeedError(
    ValueError
):
    pass


_PREFIXES = (
    "[PDF] ",
    "(PDF) ",
)

_TRAILING_SITE_SUFFIXES = (
    " - ScienceDirect",
    " · GitHub",
)


def load_scholarly_seed_queries(
    path: Path,
    *,
    plan: ProposalVerificationPlan,
    max_queries_per_requirement: int = 6,
) -> dict[
    str,
    tuple[
        str,
        ...,
    ],
]:
    if max_queries_per_requirement < 1:
        raise ValueError(
            "max_queries_per_requirement "
            "must be positive"
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise ScholarlySeedError(
            "discovery artifact must be "
            "a JSON object"
        )

    packets = payload.get(
        "packets"
    )

    lead_sets = payload.get(
        "lead_sets"
    )

    if (
            not isinstance(
                packets,
                list,
            )
            or not isinstance(
                lead_sets,
                list,
            )
            or len(packets)
            != len(lead_sets)
    ):
        raise ScholarlySeedError(
            "discovery packets and lead_sets "
            "must be aligned"
        )

    lead_queries: dict[
        str,
        tuple[
            str,
            ...,
        ],
    ] = {}

    for packet, lead_set in zip(
        packets,
        lead_sets,
        strict=True,
    ):
        if (
                not isinstance(
                    packet,
                    dict,
                )
                or not isinstance(
                    lead_set,
                    dict,
                )
        ):
            raise ScholarlySeedError(
                "invalid discovery packet "
                "or lead set"
            )

        citations = packet.get(
            "citations",
            []
        )

        citation_by_id = {
            citation.get(
                "citation_id"
            ): citation
            for citation in citations
            if isinstance(
                citation,
                dict,
            )
            and isinstance(
                citation.get(
                    "citation_id"
                ),
                str,
            )
        }

        leads = lead_set.get(
            "leads",
            []
        )

        if not isinstance(
            leads,
            list,
        ):
            raise ScholarlySeedError(
                "invalid discovery leads"
            )

        for lead in leads:
            if not isinstance(
                lead,
                dict,
            ):
                continue

            lead_id = lead.get(
                "lead_id"
            )

            if not isinstance(
                lead_id,
                str,
            ):
                continue

            queries: list[
                str
            ] = []

            for citation_id in (
                lead.get(
                    "source_citation_ids",
                    []
                )
            ):
                citation = (
                    citation_by_id.get(
                        citation_id
                    )
                )

                if citation is None:
                    continue

                title = citation.get(
                    "title"
                )

                if isinstance(
                    title,
                    str,
                ):
                    normalized = (
                        _normalize_title(
                            title
                        )
                    )

                    if normalized:
                        queries.append(
                            normalized
                        )

                url = citation.get(
                    "url"
                )

                if isinstance(
                    url,
                    str,
                ):
                    arxiv_id = (
                        _arxiv_id(
                            url
                        )
                    )

                    if arxiv_id is not None:
                        queries.append(
                            arxiv_id
                        )

            lead_queries[
                lead_id
            ] = _unique(
                queries
            )

    result: dict[
        str,
        tuple[
            str,
            ...,
        ],
    ] = {}

    for task in plan.tasks:
        if (
                task.lane
                != VerificationLane
                .SCHOLARLY_FULLTEXT
        ):
            continue

        queries: list[
            str
        ] = []

        for lead_id in task.lead_ids:
            queries.extend(
                lead_queries.get(
                    lead_id,
                    (),
                )
            )

        unique = _unique(
            queries
        )

        result[
            task.requirement
            .requirement_id
        ] = unique[
            :max_queries_per_requirement
        ]

    return result


def _normalize_title(
    value: str,
) -> str:
    result = " ".join(
        value.split()
    )

    for prefix in _PREFIXES:
        if result.startswith(
            prefix
        ):
            result = result[
                len(prefix):
            ]

    for suffix in (
        _TRAILING_SITE_SUFFIXES
    ):
        if result.endswith(
            suffix
        ):
            result = result[
                :-len(suffix)
            ]

    return result.strip()


def _arxiv_id(
    url: str,
) -> str | None:
    match = re.search(
        (
            r"arxiv\.org/"
            r"(?:abs|pdf)/"
            r"([0-9]{4}\.[0-9]{4,5})"
        ),
        url,
        flags=re.IGNORECASE,
    )

    if match is None:
        return None

    return match.group(1)


def _unique(
    values: list[
        str
    ],
) -> tuple[
    str,
    ...,
]:
    return tuple(
        dict.fromkeys(
            value
            for value in values
            if value.strip()
        )
    )
