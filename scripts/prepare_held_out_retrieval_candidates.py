import json
import os
from pathlib import Path

import httpx

from thesis_factory.artifacts.fetching import (
    ArtifactFetcher,
)
from thesis_factory.domain.source import (
    SourceRecord,
)
from thesis_factory.domain.source_text import (
    SourceTextLocation,
    SourceTextLocationKind,
)
from thesis_factory.integrations.openalex.client import (
    OpenAlexClient,
    OpenAlexSearchMode,
)
from thesis_factory.parsing.grobid import (
    GrobidTeiParser,
)


OUTPUT_PATH = Path(
    "/tmp/"
    "thesis_factory_held_out_candidates.json"
)

SEARCH_QUERIES = (
    "consumer credit scoring machine learning",
    "corporate default prediction machine learning",
    "alternative data credit scoring",
    "explainable machine learning credit risk",
)

PER_QUERY_LIMIT = 25

MIN_PARAGRAPHS = 30


BASELINE_DOIS = {
    "10.1016/j.eswa.2020.113567",
    "10.1016/j.eswa.2020.113766",
}

BASELINE_PROVIDER_IDS = {
    "https://openalex.org/W3010059221",
    "https://openalex.org/W3044323082",
}


def _grobid_location(
        locations: tuple[
            SourceTextLocation,
            ...,
        ],
) -> SourceTextLocation | None:
    return next(
        (
            location
            for location in locations
            if (
                location.kind
                == (
                    SourceTextLocationKind
                    .OPENALEX_GROBID_XML
                )
        )
        ),
        None,
    )


def _paragraph_count(
        document,
) -> int:
    return sum(
        len(section.paragraphs)
        for section
        in document.sections
    )


def _serialize_document(
        *,
        selection_query: str,
        selection_rank: int,
        source: SourceRecord,
        artifact,
        document,
) -> dict:
    paragraphs = []

    for section in document.sections:
        for paragraph in section.paragraphs:
            paragraphs.append(
                {
                    "paragraph_ordinal": (
                        paragraph.ordinal
                    ),
                    "section_ordinal": (
                        section.ordinal
                    ),
                    "section_kind": (
                        section.kind.value
                    ),
                    "heading_role": (
                        section
                        .heading_role
                        .value
                    ),
                    "section_path": list(
                        section.path
                    ),
                    "text": paragraph.text,
                }
            )

    return {
        "selection_query": (
            selection_query
        ),
        "selection_rank": (
            selection_rank
        ),
        "title": source.title,
        "doi": source.doi,
        "publication_year": (
            source.publication_year
        ),
        "provider": source.provider,
        "provider_id": (
            source.provider_id
        ),
        "artifact_sha256": (
            artifact.sha256
        ),
        "normalization_version": (
            document
            .normalization_version
        ),
        "section_count": len(
            document.sections
        ),
        "paragraph_count": len(
            paragraphs
        ),
        "paragraphs": paragraphs,
    }


def main() -> None:
    openalex_api_key = os.environ[
        "OPENALEX_API_KEY"
    ]

    discovery = OpenAlexClient(
        api_key=openalex_api_key,
        search_mode=(
            OpenAlexSearchMode.SEMANTIC
        ),
    )

    content_client = httpx.Client(
        timeout=30.0,
        follow_redirects=True,
        params={
            "api_key": openalex_api_key,
        },
    )

    fetcher = ArtifactFetcher(
        http_client=content_client,
    )

    parser = GrobidTeiParser()

    selected_documents = []

    selected_provider_ids = set(
        BASELINE_PROVIDER_IDS
    )

    selected_dois = set(
        BASELINE_DOIS
    )

    try:
        for query in SEARCH_QUERIES:
            print()
            print("=" * 100)
            print(
                "SELECTION QUERY:",
                query,
            )

            candidates = (
                discovery.search_works(
                    query,
                    per_page=(
                        PER_QUERY_LIMIT
                    ),
                )
            )

            selected = None

            for rank, source in enumerate(
                    candidates,
                    start=1,
            ):
                if (
                        source.provider_id
                        in selected_provider_ids
                ):
                    continue

                if (
                        source.doi is not None
                        and source.doi
                        in selected_dois
                ):
                    continue

                # Keep the held-out corpus
                # bibliographically pin-able.
                if source.doi is None:
                    continue

                try:
                    locations = (
                        discovery
                        .get_text_locations(
                            source
                        )
                    )

                    location = (
                        _grobid_location(
                            locations
                        )
                    )

                    if location is None:
                        continue

                    artifact = fetcher.fetch(
                        location
                    )

                    document = parser.parse(
                        artifact
                    )

                except (
                        httpx.HTTPError,
                        ValueError,
                ) as error:
                    print(
                        "  SKIP:",
                        rank,
                        source.title,
                        "-",
                        type(error).__name__,
                    )
                    continue

                paragraph_count = (
                    _paragraph_count(
                        document
                    )
                )

                if (
                        paragraph_count
                        < MIN_PARAGRAPHS
                ):
                    print(
                        "  SKIP:",
                        rank,
                        source.title,
                        "- only",
                        paragraph_count,
                        "paragraphs",
                    )
                    continue

                selected = (
                    _serialize_document(
                        selection_query=query,
                        selection_rank=rank,
                        source=source,
                        artifact=artifact,
                        document=document,
                    )
                )

                selected_provider_ids.add(
                    source.provider_id
                )

                selected_dois.add(
                    source.doi
                )

                break

            if selected is None:
                raise RuntimeError(
                    "No eligible held-out "
                    "document found for query: "
                    f"{query}"
                )

            selected_documents.append(
                selected
            )

            print(
                "  SELECTED:",
                selected["title"],
            )

            print(
                "  DOI:",
                selected["doi"],
            )

            print(
                "  OPENALEX:",
                selected[
                    "provider_id"
                ],
            )

            print(
                "  SEARCH RANK:",
                selected[
                    "selection_rank"
                ],
            )

            print(
                "  SHA256:",
                selected[
                    "artifact_sha256"
                ],
            )

            print(
                "  SECTIONS:",
                selected[
                    "section_count"
                ],
            )

            print(
                "  PARAGRAPHS:",
                selected[
                    "paragraph_count"
                ],
            )

    finally:
        discovery.close()
        content_client.close()

    payload = {
        "name": (
            "credit-risk-held-out-"
            "candidate-corpus-v1"
        ),
        "selection_protocol": {
            "discovery_provider": (
                "OpenAlex"
            ),
            "discovery_mode": (
                "SEMANTIC"
            ),
            "queries": list(
                SEARCH_QUERIES
            ),
            "per_query_limit": (
                PER_QUERY_LIMIT
            ),
            "selection_rule": (
                "For each query in fixed "
                "order, select the first "
                "previously unseen result "
                "with a DOI, downloadable "
                "OpenAlex GROBID XML, "
                "successful grobid-tei-v1 "
                "normalization, and at least "
                f"{MIN_PARAGRAPHS} paragraphs."
            ),
            "excluded_baseline_dois": (
                sorted(
                    BASELINE_DOIS
                )
            ),
            "retrieval_systems_used_for_selection": [],
        },
        "documents": (
            selected_documents
        ),
    }

    OUTPUT_PATH.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
        )

    print()
    print("=" * 100)
    print(
        "SELECTED DOCUMENTS:",
        len(selected_documents),
    )

    print(
        "OUTPUT:",
        OUTPUT_PATH,
    )

    print()
    print(
        "IMPORTANT: BM25, Voyage, and RRF "
        "have not been run against these "
        "documents."
    )


if __name__ == "__main__":
    main()