from collections.abc import Mapping

from thesis_factory.artifacts.fetching import (
    ArtifactFetcher,
)
from thesis_factory.domain.evidence_acquisition import (
    EvidenceRequirement,
)
from thesis_factory.domain.scholarly_verification import (
    ScholarlySourceAudit,
)
from thesis_factory.domain.source import (
    SourceRecord,
)
from thesis_factory.domain.source_text import (
    SourceTextLocationKind,
)
from thesis_factory.integrations.openalex.client import (
    OpenAlexClient,
)
from thesis_factory.parsing.grobid import (
    GrobidTeiParser,
)
from thesis_factory.research.scholarly_evidence_execution import (
    ScholarlyDocumentCandidate,
    ScholarlyDocumentDiscovery,
)
from thesis_factory.verification.identity import (
    IdentityStatus,
)
from thesis_factory.workflows.source_verification import (
    DoiRegistry,
    verify_source,
)


class OpenAlexVerifiedDocumentProvider:
    def __init__(
        self,
        *,
        searcher: OpenAlexClient,
        registry: DoiRegistry,
        fetcher: ArtifactFetcher,
        parser: GrobidTeiParser,
        seed_queries_by_requirement_id: Mapping[
            str,
            tuple[
                str,
                ...,
            ],
        ] | None = None,
        search_limit: int = 5,
        max_search_queries: int = 4,
        max_documents: int = 3,
    ) -> None:
        if search_limit < 1:
            raise ValueError(
                "search_limit must be positive"
            )

        if max_search_queries < 1:
            raise ValueError(
                "max_search_queries must be positive"
            )

        if max_documents < 1:
            raise ValueError(
                "max_documents must be positive"
            )

        self._searcher = searcher
        self._registry = registry
        self._fetcher = fetcher
        self._parser = parser
        self._seed_queries = dict(
            seed_queries_by_requirement_id
            or {}
        )
        self._search_limit = search_limit
        self._max_search_queries = (
            max_search_queries
        )
        self._max_documents = (
            max_documents
        )

    def discover(
        self,
        *,
        requirement: EvidenceRequirement,
    ) -> ScholarlyDocumentDiscovery:
        errors: list[str] = []

        queries = list(
            self._seed_queries.get(
                requirement.requirement_id,
                (),
            )
        )

        # Keep a requirement-level fallback, but run
        # discovery-citation titles first. The previous
        # implementation searched only this long question,
        # which produced broad topical papers instead of
        # the already-discovered target sources.
        if (
                requirement.question
                not in queries
        ):
            queries.append(
                requirement.question
            )

        queries = queries[
            :self._max_search_queries
        ]

        discovered_by_key: dict[
            str,
            SourceRecord,
        ] = {}

        for query in queries:
            try:
                discovered = (
                    self._searcher
                    .search_works(
                        query,
                        per_page=(
                            self._search_limit
                        ),
                    )
                )
            except Exception as error:
                errors.append(
                    _error_text(
                        (
                            "OpenAlex search failed "
                            f"for query {query!r}"
                        ),
                        error,
                    )
                )
                continue

            for source in discovered:
                discovered_by_key.setdefault(
                    _source_key(
                        source
                    ),
                    source,
                )

        documents: list[
            ScholarlyDocumentCandidate
        ] = []

        audits: list[
            ScholarlySourceAudit
        ] = []

        for source in (
            discovered_by_key.values()
        ):
            if (
                len(documents)
                >= self._max_documents
            ):
                break

            try:
                verification = verify_source(
                    source,
                    registry=self._registry,
                )
            except Exception as error:
                audits.append(
                    ScholarlySourceAudit(
                        source=source,
                        usable_fulltext=False,
                        note=_error_text(
                            "DOI verification failed",
                            error,
                        ),
                    )
                )
                continue

            if (
                verification.identity is None
                or verification.identity.status
                != IdentityStatus.CONFIRMED
            ):
                audits.append(
                    ScholarlySourceAudit(
                        source=source,
                        registry_source=(
                            verification.registry_source
                        ),
                        usable_fulltext=False,
                        note=(
                            "Source identity was not "
                            "confirmed by DOI metadata."
                        ),
                    )
                )
                continue

            try:
                locations = (
                    self._searcher
                    .get_text_locations(
                        source
                    )
                )
            except Exception as error:
                audits.append(
                    ScholarlySourceAudit(
                        source=source,
                        registry_source=(
                            verification.registry_source
                        ),
                        usable_fulltext=False,
                        note=_error_text(
                            (
                                "Full-text location "
                                "lookup failed"
                            ),
                            error,
                        ),
                    )
                )
                continue

            location = (
                _select_grobid_location(
                    locations
                )
            )

            if location is None:
                audits.append(
                    ScholarlySourceAudit(
                        source=source,
                        registry_source=(
                            verification.registry_source
                        ),
                        usable_fulltext=False,
                        note=(
                            "Identity confirmed, but "
                            "OpenAlex exposed no GROBID "
                            "XML full text. PDF-only "
                            "sources are intentionally "
                            "not promoted by this "
                            "executor yet."
                        ),
                    )
                )
                continue

            try:
                artifact = (
                    self._fetcher.fetch(
                        location
                    )
                )

                document = (
                    self._parser.parse(
                        artifact
                    )
                )
            except Exception as error:
                audits.append(
                    ScholarlySourceAudit(
                        source=source,
                        registry_source=(
                            verification.registry_source
                        ),
                        fulltext_url=(
                            location.url
                        ),
                        usable_fulltext=False,
                        note=_error_text(
                            (
                                "Full-text fetch or "
                                "normalization failed"
                            ),
                            error,
                        ),
                    )
                )
                continue

            documents.append(
                ScholarlyDocumentCandidate(
                    source=source,
                    registry_source=(
                        verification.registry_source
                    ),
                    document=document,
                    fulltext_url=(
                        location.url
                    ),
                )
            )

            audits.append(
                ScholarlySourceAudit(
                    source=source,
                    registry_source=(
                        verification.registry_source
                    ),
                    fulltext_url=(
                        location.url
                    ),
                    artifact_sha256=(
                        document.artifact_sha256
                    ),
                    usable_fulltext=True,
                    note=(
                        "Identity confirmed and "
                        "GROBID XML normalized."
                    ),
                )
            )

        return ScholarlyDocumentDiscovery(
            documents=tuple(
                documents
            ),
            source_audits=tuple(
                audits
            ),
            errors=tuple(
                errors
            ),
        )


def _source_key(
    source: SourceRecord,
) -> str:
    if source.doi is not None:
        return (
            "doi:"
            + source.doi.casefold()
        )

    return (
        f"{source.provider.casefold()}:"
        f"{source.provider_id}"
    )


def _select_grobid_location(
    locations,
):
    for location in locations:
        if (
            location.kind
            == SourceTextLocationKind
            .OPENALEX_GROBID_XML
        ):
            return location

    return None


def _error_text(
    context: str,
    error: Exception,
) -> str:
    message = " ".join(
        str(error).split()
    )

    if not message:
        message = (
            error.__class__.__name__
        )

    return (
        f"{context}: "
        f"{error.__class__.__name__}: "
        f"{message}"
    )[:1200]
